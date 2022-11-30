
from datetime import datetime

from json import JSONDecodeError

from sqlalchemy.future import select

from passlib.hash import pbkdf2_sha1

from starlette.exceptions import HTTPException
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.status import HTTP_400_BAD_REQUEST

from db_config.storage_config import engine, async_session

from account.models import User

from mail.email import send_mail

from .token import (
    encode_verification_token,
    create_token,
    mail_verify,
)


templates = Jinja2Templates(directory="templates")


async def user_register(
    request
):
    template = "/auth/register.html"

    async with async_session() as session:

        if request.method == "POST":
            form = await request.form()
            username = form["username"]
            email = form["email"]
            password = form["password"]

            try:
                payload = await request.form()

            except JSONDecodeError as exc:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail="Can't parse json request"
                ) from exc

            username = payload["username"]
            email = payload["email"]
            password = pbkdf2_sha1.hash(payload["password"])

            #..
            result = await session.execute(
                select(User)
                .where(User.email == email)
            )
            user_exist = result.scalars().first()
            #..

            if user_exist:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail="Уже зарегистрирован"
                )

            new_user = User()
            new_user.username = username
            new_user.email = email
            new_user.password = password

            session.add(new_user)
            session.refresh(new_user)
            await session.commit()

            context = {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
            }

            #..
            email_token = await encode_verification_token(
                {
                    "email": email,
                    "get_expired_token": 1,
                }
            )

            await send_mail(
                f"Follow the link, confirm your email - https://starlette-web.herokuapp.com/account/email-verify?token={email_token}"
            )

            response = RedirectResponse("/", status_code=302)
            response.token = context
            return response

        return templates.TemplateResponse(template, {"request": request})
    await engine.dispose()


async def user_login(
    request
):
    template = "/auth/login.html"

    async with async_session() as session:

        if request.method == "POST":
            try:
                payload = await request.form()

            except JSONDecodeError as exc:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail="Can't parse json request"
                ) from exc

            email = payload["email"]
            password = payload["password"]
            #..
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalars().first()
            #..
            if user:
                if not user.email_verified:
                    raise HTTPException(
                        401,
                        "Электронная почта не подтверждена. Проверьте свою почту, чтобы узнать, как пройти верификацию.",
                    )

                if pbkdf2_sha1.verify(password, user.password):
                    #..
                    user.last_login_date = datetime.now()
                    #..
                    session.add(user)
                    await session.commit()

                    access_token = await create_token(
                        {
                            "user_id": user.id,
                            "email": user.email,
                            "username": user.username,
                            "get_expired_token": 1,
                        }
                    )
                    response = RedirectResponse("/", status_code=302)
                    #..
                    response.set_cookie(
                        key="access_token", value=f"JWT {access_token}", httponly=True
                    )
                    #..
                    return response

                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid login or password",
                )
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Invalid login or password"
            )
        return templates.TemplateResponse(template, {"request": request})
    await engine.dispose()


async def user_logout(
    request
):
    template = "/auth/logout.html"

    if request.method == "POST":
        if request.user:
            response = RedirectResponse("/", status_code=302)
            response.delete_cookie(key="access_token", path="/")
            #..
            return response

        return templates.TemplateResponse(template, {"request": request})
    return templates.TemplateResponse(template, {"request": request})


async def verify_email(
    request
):

    if request.method == "GET":
        response = await mail_verify(request)
        return response


async def resend_email(
    request
):
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

            #..
            email_token = await encode_verification_token(
                {
                    "email": email,
                    "get_expired_token": 1,
                }
            )

            await send_mail(
                f"Follow the link, confirm your email - https://starlette-web.herokuapp.com/account/email-verify?token={email_token}"
            )

        return templates.TemplateResponse(template, {"request": request})
    await engine.dispose()
