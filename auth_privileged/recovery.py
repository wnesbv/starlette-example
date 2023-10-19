
import jwt

from passlib.hash import pbkdf2_sha1

from starlette.exceptions import HTTPException
from starlette.templating import Jinja2Templates
from starlette.responses import Response, RedirectResponse

from mail.verify import verify_mail
from account.models import User

from db_config.storage_config import engine, async_session
from options_select.opt_slc import left_right_first

from .token import encode_reset_password, decode_reset_password


templates = Jinja2Templates(directory="templates")


async def reset_password(
    request
):

    template = "/auth/reset-password.html"

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
            # ...
            token = await encode_reset_password(email)
            verify = email
            await verify_mail(
                f"Follow the link, confirm your email - http://127.0.0.1:8000/account/reset-password-confirm?token={token}", verify
            )

            response = Response("Ok..! Link to password recovery. Check email")
            return response

        return templates.TemplateResponse(
            template, {"request": request}
        )
    await engine.dispose()


async def reset_password_verification(
    request
):

    async with async_session() as session:

        email = await decode_reset_password(request)
        # ..
        user = await left_right_first(session, User, User.email, email)
        # ...
        if not user:
            raise HTTPException(
                401,
                "Недействительный пользователь..! Пожалуйста, создайте учетную запись",
            )


        form = await request.form()
        user.password = pbkdf2_sha1.hash(form["password"])
        await session.commit()

    await engine.dispose()


async def reset_password_confirm(
    request
):
    template = "auth/reset-password-confirm.html"
    if request.method == "GET":
        return templates.TemplateResponse(
            template,
            {"request": request},
        )
    if request.method == "POST":
        await reset_password_verification(request)
        response = RedirectResponse("/account/login", status_code=302)
        return response
