
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath

import os, jwt

from sqlalchemy import update as sqlalchemy_update, delete

from sqlalchemy.future import select

from passlib.hash import pbkdf2_sha1

from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.authentication import requires

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from account.models import User
from item.img import FileType, BASE_DIR
from mail.verify import verify_mail

from .token import (
    mail_verify,
)


key = settings.SECRET_KEY
algorithm = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES

templates = Jinja2Templates(directory="templates")


async def user_register(request):
    template = "/auth/register.html"

    async with async_session() as session:
        if request.method == "POST":
            form = await request.form()
            name = form["name"]
            email = form["email"]
            password = form["password"]
            # ..
            stmt_name = await session.execute(select(User).where(User.name == name))
            name_exist = stmt_name.scalars().first()
            stmt_email = await session.execute(select(User).where(User.email == email))
            email_exist = stmt_email.scalars().first()
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
            session.refresh(new)
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


async def img_creat(
    request, image_url
):

    save_path = f"./static/upload/{request.user.email}"
    file_path = f"{save_path}/{image_url.filename}"

    ext = PurePosixPath(image_url.filename).suffix
    if ext not in (".png", ".jpg", ".jpeg"):
        raise HTTPException(
            status_code=400,
            detail="Format files: png, jpg, jpeg ..!",
        )
    if Path(file_path).exists():
        raise HTTPException(
            status_code=400,
            detail="Error..! File exists..!"
        )

    os.makedirs(save_path, exist_ok=True)

    with open(f"{file_path}", "wb") as fle:
        fle.write(image_url.file.read())

    return file_path.replace(".", "", 1)


@requires("authenticated", redirect="user_login")
# ...
async def user_update(request):

    id = request.path_params["id"]
    template = "/auth/update.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(
            select(User).where(
                User.id == id,
            )
        )
        obj = stmt.scalars().first()
        # ..
        context = {
            "request": request,
            "obj": obj,
        }
        # ...
        if request.method == "GET":
            if obj and request.user.user_id == obj.id:
                return templates.TemplateResponse(template, context)

            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            name = form["name"]
            image_url = form["image_url"]
            del_obj = form.get("del_bool")
            # ...
            if image_url.filename == "":
                query = (
                    sqlalchemy_update(User)
                    .where(User.id == id)
                    .values(
                        name=name,
                        image_url=obj.image_url,
                        modified_at=datetime.now()
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(query)
                await session.commit()

                if del_obj:

                    if Path(f".{obj.image_url}").exists():
                        Path.unlink(f".{obj.image_url}")

                    fle_not = (
                        sqlalchemy_update(User)
                        .where(User.id == id)
                        .values(
                            image_url=None,
                            modified_at=datetime.now()
                        )
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

            file_query = (
                sqlalchemy_update(User)
                .where(User.id == id)
                .values(
                    name=name,
                    image_url = await img_creat(request, image_url),
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()

            return RedirectResponse(
                f"/account/details/{id}",
                status_code=302,
            )

    await engine.dispose()


async def user_list(request):
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
    id = request.path_params["id"]
    template = "/auth/details.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(
            select(User).where(
                User.id == id,
            )
        )
        result = stmt.scalars().first()
        # ..
        context = {
            "request": request,
            "result": result,
        }
        # ...
        if request.method == "GET":
            if result:
                return templates.TemplateResponse(template, context)
        return RedirectResponse("/account/list", status_code=302)
    await engine.dispose()


async def user_login(request):
    template = "/auth/login.html"

    async with async_session() as session:
        if request.method == "POST":
            form = await request.form()
            email = form["email"]
            password = form["password"]
            # ..
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalars().first()
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

                    payload = {
                        "user_id": user.id,
                        "name": user.name,
                        "email": user.email,
                    }

                    # ..
                    visited = jwt.encode(payload, key, algorithm)
                    response = RedirectResponse("/", status_code=302)
                    response.set_cookie(
                        "visited",
                        visited,
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


async def user_logout(request):
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
