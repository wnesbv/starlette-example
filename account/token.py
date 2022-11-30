
from datetime import datetime, timedelta

from sqlalchemy.future import select

import jwt

from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse

from account.models import User
from db_config.storage_config import engine, async_session
from db_config.settings import settings

secret_key = settings.SECRET_KEY


async def create_token(token_config: dict) -> str:

    payload = {
        "username": token_config["username"],
        "user_id": token_config["user_id"],
        "email": token_config["email"],
        "iat": datetime.utcnow(),
    }

    if "get_expired_token" in token_config:
        payload["sub"] = "access_token"

    token = jwt.encode(
        payload,
        secret_key,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


async def encode_verification_token(token_config: dict) -> str:

    payload = {
        "exp": datetime.utcnow()
        + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRY_MINUTES),
        "iat": datetime.utcnow(),
        "scope": "email_verification",
    }

    if "get_expired_token" in token_config:
        payload["sub"] = token_config["email"]

    token = jwt.encode(
        payload,
        secret_key,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


async def verify_decode(
    request
):
    token = request.query_params["token"]

    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=settings.JWT_ALGORITHM,
        )

        if payload["scope"] == "email_verification":
            email = payload["sub"]
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

        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalars().first()

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

async def encode_reset_password(token_config: dict) -> str:

    payload = {
        "exp": datetime.utcnow()
        + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRY_MINUTES),
        "iat": datetime.utcnow(),
        "scope": "reset_password",
    }

    if "get_expired_token" in token_config:
        payload["sub"] = token_config["email"]

    token = jwt.encode(
        payload,
        secret_key,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


async def decode_reset_password(
    request
):
    token = request.query_params["token"]

    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=settings.JWT_ALGORITHM,
        )

        if payload["scope"] == "reset_password":
            email = payload["sub"]
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
