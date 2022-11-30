
import jwt

from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
)

from db_config.settings import settings


class JWTUser(BaseUser):
    def __init__(
        self, username: str, user_id: int, email: str, token: str, payload: dict
    ) -> None:
        self.username = username
        self.user_id = user_id
        self.email = email
        self.token = token
        self.payload = payload

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    def __str__(self) -> str:
        return (
            f"JWT user: username={self.username}, id={self.user_id}, email={self.email}"
        )


class JWTAuthenticationBackend(AuthenticationBackend):
    def __init__(
        self,
        secret_key: str,
        algorithm: str = settings.JWT_ALGORITHM,
        prefix: str = settings.JWT_PREFIX,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix


    @classmethod
    def get_token_from_header(cls, authorization: str, prefix: str):

        try:
            scheme, token = authorization.split()
        except ValueError as exc:
            raise AuthenticationError(
                "Could not separate Authorization scheme and token"
            ) from exc

        if scheme.lower() != prefix.lower():
            raise AuthenticationError(f"Authorization scheme {scheme} is not supported")

        return token


    async def authenticate(self, conn):

        if "access_token" not in conn.cookies:
            return None

        authorization = conn.cookies.get("access_token")
        #..
        token = self.get_token_from_header(
            authorization=authorization, prefix=self.prefix
        )

        try:
            payload = jwt.decode(
                token, key=str(self.secret_key), algorithms=self.algorithm
            )

        except jwt.InvalidTokenError as exc:
            raise AuthenticationError("Invalid JWT token") from exc

        return (
            AuthCredentials(["authenticated"]),
            JWTUser(
                username=payload["username"],
                user_id=payload["user_id"],
                email=payload["email"],
                payload=payload,
                token=token,
            ),
        )
