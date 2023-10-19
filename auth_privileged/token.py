
from datetime import datetime, timedelta

import jwt

from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse


from account.models import User

from db_config.storage_config import engine, async_session
from db_config.settings import settings

from options_select.opt_slc import left_right_first


key = settings.SECRET_KEY
algorithm = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES


async def verify_decode(
    request
):
    payload = request.query_params["token"]

    try:
        token = jwt.decode(
            payload,
            key,
            algorithm,
        )

        if token["scope"] == "email_verification":
            email = token["email"]
            return email

        raise HTTPException(401, "Invalid scope for token")

    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            401, "Email token expired"
        ) from exc
    except jwt.InvalidTokenError:
        raise HTTPException(
            401, "Invalid email token"
        ) from exc


async def mail_verify(
    request
):
    async with async_session() as session:

        email = await verify_decode(request)
        # ..
        user = await left_right_first(session, User, User.email, email)
        # ..
        if not user:
            raise HTTPException(
                401, "Недействительный пользователь..! Пожалуйста, создайте учетную запись"
            )

        if user.email_verified:
            raise HTTPException(
                304, "Электронная почта пользователя уже подтверждена!"
            )

        user.email_verified = True
        user.is_active = True
        await session.commit()

        response = RedirectResponse(
            "/", status_code=302
        )
        return response
        # return {"msg": "Электронная почта успешно подтверждена"}
    await engine.dispose()


# ...

async def encode_reset_password(email):

    payload = {
        "email": email,
        "exp": datetime.utcnow()
        + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRY_MINUTES),
        "iat": datetime.utcnow(),
        "scope": "reset_password",
    }
    token = jwt.encode(
        payload,
        key,
        algorithm
    )
    return token


async def decode_reset_password(
    request
):
    token = request.query_params["token"]

    try:
        payload = jwt.decode(
            token,
            key,
            algorithm,
        )

        if payload["scope"] == "reset_password":
            email = payload["email"]
            return email

        raise HTTPException(401, "Invalid scope for token")

    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            401, "Email token expired"
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            401, "Invalid email token"
        ) from exc
