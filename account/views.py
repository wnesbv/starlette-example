from datetime import datetime, timedelta
from pathlib import Path

import os, jwt, functools

from sqlalchemy import update as sqlalchemy_update, false, and_

from sqlalchemy.future import select

from passlib.hash import pbkdf2_sha1

from starlette.exceptions import HTTPException
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse
from starlette.status import HTTP_400_BAD_REQUEST

from admin import img
from account.models import User
from mail.verify import verify_mail

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from options_select.opt_slc import left_right_first

from auth_privileged.opt_slc import get_privileged_user

from .token import mail_verify
from .opt_slc import visited


key = settings.SECRET_KEY
algorithm = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES

templates = Jinja2Templates(directory="templates")


async def user_register(request):
    # ..
    template = "/auth/register.html"

    async with async_session() as session:
        if request.method == "POST":
            form = await request.form()
            name = form["name"]
            email = form["email"]
            password = form["password"]
            # ..
            name_exist = await left_right_first(session, User, User.name, name)
            email_exist = await left_right_first(session, User, User.email, email)
            # ..
            if name_exist:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="name already registered..!",
                )
            if email_exist:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="email already registered..!",
                )
            new = User()
            new.name = name
            new.email = email
            new.password = pbkdf2_sha1.hash(password)
            new.created_at = datetime.now()

            session.add(new)
            await session.commit()
            # ..
            payload = {
                "email": email,
                "exp": datetime.utcnow()
                + timedelta(minutes=int(EMAIL_TOKEN_EXPIRY_MINUTES)),
                "iat": datetime.utcnow(),
                "scope": "email_verification",
            }
            token = jwt.encode(payload, key, algorithm)
            # ..
            verify = email
            await verify_mail(
                f"Follow the link, confirm your email - http://127.0.0.1:8000/account/email-verify?token={token}",
                verify,
            )
            return RedirectResponse(
                "/messages?msg=Go to the specified email address..", status_code=302
            )

        return templates.TemplateResponse(template, {"request": request})
    await engine.dispose()


async def user_login(request):
    # ..
    if request.method == "GET":
        template = "/auth/login.html"
        return templates.TemplateResponse(template, {"request": request})
    #...
    if request.method == "POST":
        async with async_session() as session:
            # ..
            form = await request.form()
            # ..
            email = form["email"]
            password = form["password"]
            # ..
            stmt = await session.execute(
                select(User).where(
                    and_(User.email == email, User.privileged == false())
                )
            )
            user = stmt.scalars().first()
            # ..
            if user:
                if not user.email_verified:
                    raise HTTPException(
                        401,
                        "Электронная почта не подтверждена. Проверьте свою почту, чтобы узнать, как пройти верификацию.",
                    )

                if pbkdf2_sha1.verify(password, user.password):
                    # ..
                    user.last_login_date = datetime.now()
                    # ..
                    session.add(user)
                    await session.commit()
                    # ..
                    payload = {
                        "user_id": user.id,
                        "name": user.name,
                        "email": email,
                    }
                    token = jwt.encode(payload, key, algorithm)
                    # ..
                    response = RedirectResponse("/", status_code=302)
                    response.set_cookie(
                        key="visited", value=token, path="/", httponly=True
                    )
                    # ..
                    return response

                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid password",
                )
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Invalid login"
            )

        await engine.dispose()


@visited()
# ...
async def user_update(request):
    # ..
    basewidth = 256
    id = request.path_params["id"]
    template = "/auth/update.html"

    async with async_session() as session:
        # ..
        i = await left_right_first(session, User, User.id, id)
        # ..
        if request.method == "GET":
            if request.user.user_id == i.id:
                context = {
                    "request": request,
                    "i": i,
                }
                return templates.TemplateResponse(template, context)

            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            name = form["name"]
            file = form["file"]
            del_obj = form.get("del_bool")
            # ..

            if file.filename == "":
                query = (
                    sqlalchemy_update(User)
                    .where(User.id == id)
                    .values(name=name, file=i.file, modified_at=datetime.now())
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(query)
                await session.commit()

                if del_obj:
                    if Path(f".{i.file}").exists():
                        Path.unlink(f".{i.file}")

                    fle_not = (
                        sqlalchemy_update(User)
                        .where(User.id == id)
                        .values(file=None, modified_at=datetime.now())
                        .execution_options(synchronize_session="fetch")
                    )
                    await session.execute(fle_not)
                    await session.commit()

                    return RedirectResponse(
                        f"/account/details/{id}",
                        status_code=302,
                    )
                return RedirectResponse(
                    f"/account/details/{id }",
                    status_code=302,
                )
            # ..
            email = request.user.email
            file_query = (
                sqlalchemy_update(User)
                .where(User.id == id)
                .values(
                    name=name,
                    file=await img.user_img_creat(file, email, basewidth),
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(file_query)
            await session.commit()

            return RedirectResponse(
                f"/account/details/{id}",
                status_code=302,
            )

    await engine.dispose()


@visited()
# ...
async def user_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/auth/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            if request.user.user_id == id:
                return templates.TemplateResponse(template, {"request": request})
            return PlainTextResponse("You are banned - this is not your account..!")

        # ...
        if request.method == "POST":
            # ..
            i = await left_right_first(session, User, User.id, id)
            await img.del_user(i.email)
            # ..
            await session.delete(i)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/account/list",
                status_code=302,
            )
            return response
    await engine.dispose()


@visited()
# ...
async def user_logout(request):
    # ..
    template = "/auth/logout.html"

    if request.method == "POST":
        if request.user:
            response = RedirectResponse("/", status_code=302)
            response.delete_cookie(key="visited", path="/")
            # ..
            return response

        return templates.TemplateResponse(template, {"request": request})
    return templates.TemplateResponse(template, {"request": request})


async def verify_email(request):
    if request.method == "GET":
        response = await mail_verify(request)
        return response


async def resend_email(request):
    template = "/auth/resend.html"
    async with async_session() as session:
        if request.method == "POST":
            form = await request.form()
            email = form["email"]
            # ..
            user = await left_right_first(session, User, User.email, email)
            # ..
            if not user:
                raise HTTPException(
                    401, "Пользователь с таким адресом электронной почты не существует!"
                )
            if user.email_verified:
                raise HTTPException(400, "Электронная почта уже проверена!")
            # ..
            payload = {
                "email": email,
                "exp": datetime.utcnow()
                + timedelta(minutes=int(EMAIL_TOKEN_EXPIRY_MINUTES)),
                "iat": datetime.utcnow(),
            }
            token = jwt.encode(payload, key, algorithm)
            verify = email
            await verify_mail(
                f"Follow the link, confirm your email - https://starlette-web.herokuapp.com/account/email-verify?token={token}",
                verify,
            )

        return templates.TemplateResponse(template, {"request": request})
    await engine.dispose()


async def user_list(request):
    # ..
    template = "/auth/list.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(select(User))
        result = stmt.scalars().all()
        # ..
        context = {
            "request": request,
            "result": result,
        }
        # ...
        if request.method == "GET":
            return templates.TemplateResponse(template, context)
    await engine.dispose()


async def user_detail(request):
    # ..
    id = request.path_params["id"]
    template = "/auth/details.html"

    async with async_session() as session:
        # ..
        i = await left_right_first(session, User, User.id, id)
        prv = await get_privileged_user(request, session)
        # ..
        if request.method == "GET":
            if i:
                context = {
                    "request": request,
                    "i": i,
                    "prv": prv,
                }
                return templates.TemplateResponse(template, context)
            return RedirectResponse("/account/list", status_code=302)
    await engine.dispose()
