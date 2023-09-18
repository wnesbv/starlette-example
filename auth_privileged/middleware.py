
import jwt

from starlette.authentication import (
    AuthCredentials,
    BaseUser,
)

from .auth import AuthenticationBackend


class PrivilegedUser(BaseUser):
    def __init__(
        self, token: str, prv_key: int, payload: dict) -> None:
        self.token = token
        self.prv_key = prv_key
        self.payload = payload


    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.prv_key

    def __str__(self) -> str:
        return (
            f"prv: prv_key={self.prv_key}"
        )


class PrivilegedBackend(AuthenticationBackend):
    def __init__(
        self,
        key: str,
        algorithm: str,
    ):
        self.key = key
        self.algorithm = algorithm

    async def auth_privileged(self, conn):
        if "privileged" not in conn.cookies:
            return None

        token = conn.cookies.get("privileged")
        payload = jwt.decode(
            token, key=str(self.key), algorithms=self.algorithm
        )

        return (
            AuthCredentials("auth_prv"),
            PrivilegedUser(
                token=token,
                payload=payload,
                prv_key=payload["prv_key"],
            ),
        )
