
from pathlib import Path
from datetime import datetime, timedelta

import os, jwt, json, string, secrets, functools

from sqlalchemy import update as sqlalchemy_update, delete, true, and_
from sqlalchemy.future import select

from passlib.hash import pbkdf2_sha1

from starlette.exceptions import HTTPException
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse
from starlette.status import HTTP_400_BAD_REQUEST

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from options_select.opt_slc import for_id

from admin import img

from account.models import User

from mail.verify import verify_mail
from .token import mail_verify
from .models import Privileged
from .opt_slc import get_random_string, privileged, get_token_privileged, get_privileged_user

key = settings.SECRET_KEY
algorithm = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES

templates = Jinja2Templates(directory="templates")


# ...
async def prv_login(request):
    # ..
    template = "/auth/login.html"

    async with async_session() as session:
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            email = form["email"]
            password = form["password"]
            # ..
            stmt = await session.execute(
                select(User)
                .where(
                    and_(User.email == email, User.privileged, true())
                )
            )
            user = stmt.scalars().first()
            # ..
            if user:
                # ..
                stmt = await session.execute(
                    select(Privileged)
                    .where(Privileged.prv_in == user.id)
                )
                prv = stmt.scalars().first()
                # ..
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
                    await session.flush()
                    # ..
                    if prv:
                        query = delete(Privileged).where(Privileged.id == prv.id)
                        await session.execute(query)
                        await session.commit()
                    prv_key = await get_random_string()
                    # ..
                    new = Privileged()
                    new.prv_key = prv_key
                    new.prv_in = user.id
                    # ..
                    session.add(new)
                    await session.commit()
                    # ..
                    payload = {
                        "prv_key": prv_key,
                    }
                    token = jwt.encode(payload, key, algorithm)
                    response = RedirectResponse("/", status_code=302)
                    response.set_cookie(
                        "privileged",
                        token,
                        path="/",
                        httponly=True,
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
        return templates.TemplateResponse(template, {"request": request})
    await engine.dispose()


@privileged()
# ...
async def prv_logout(request):
    # ..
    template = "/auth/logout.html"

    if request.method == "GET":
        return templates.TemplateResponse(
            template, {"request": request}
        )
    # ...
    if request.method == "POST":
        prv_key = await get_token_privileged(request)
        async with async_session() as session:
            stmt = await session.execute(
                select(Privileged).where(Privileged.prv_key == prv_key)
            )
            prv = stmt.scalars().first()
            query = delete(Privileged).where(Privileged.id == prv.id)
            await session.execute(query)
            await session.commit()
        await engine.dispose()
        # ..
        response = RedirectResponse("/", status_code=302)
        response.delete_cookie(key="privileged", path="/")
        # ..
        return response
# ...


@privileged()
# ...
async def prv_update(request):
    # ..
    basewidth = 256
    id = request.path_params["id"]
    template = "/auth/update.html"

    async with async_session() as session:
        # ..
        i = await for_id(session, User, id)
        prv = await get_privileged_user(request, session)
        # ..
        if request.method == "GET":
            if prv == i:
                context = {
                    "request": request,
                    "i": i,
                    "prv": prv,
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


@privileged()
# ...
async def prv_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/auth/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            prv = await get_privileged_user(request, session)
            if prv.id == id:
                return templates.TemplateResponse(template, {"request": request})
            return PlainTextResponse("You are banned - this is not your account..!")

        # ...
        if request.method == "POST":
            # ..
            i = await for_id(session, User, id)
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

            result = await session.execute(select(User).where(User.email == email))
            user = result.scalars().first()

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


@privileged()
# ...
async def prv_list(request):
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


@privileged()
# ...
async def prv_detail(request):
    # ..
    id = request.path_params["id"]
    template = "/auth/details.html"

    async with async_session() as session:
        # ..
        i = await for_id(session, User, id)
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
