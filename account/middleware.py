
import jwt

from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    BaseUser,
)


class JwtUser(BaseUser):
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


class JwtBackend(AuthenticationBackend):
    def __init__(
        self,
        key: str,
        algorithm: str,
    ):
        self.key = key
        self.algorithm = algorithm

    async def authenticate(self, conn):
        if "visited" not in conn.cookies:
            return None

        token = conn.cookies.get("visited")
        payload = jwt.decode(
            token, key=str(self.key), algorithms=self.algorithm
        )

        return (
            AuthCredentials("authenticated"),
            JwtUser(
                username=payload["name"],
                user_id=payload["user_id"],
                email=payload["email"],
                payload=payload,
                token=token,
            ),
        )
