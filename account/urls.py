
from starlette.routing import Route

from .views import (
    user_login,
    user_register,
    user_logout,
    verify_email,
    resend_email,

)
from .recovery import (
    reset_password,
    reset_password_confirm,
)


routes = [
    Route(
        "/register",
        endpoint=user_register,
        methods=["GET", "POST", "OPTIONS"],
        name="user__register",
    ),
    Route(
        "/login",
        endpoint=user_login,
        methods=["GET", "POST", "OPTIONS"],
        name="user_login",
    ),
    Route(
        "/logout",
        endpoint=user_logout,
        methods=["GET", "POST", "OPTIONS"],
        name="user_logout",
    ),
    # ...
    Route(
        "/email-verify/",
        endpoint=verify_email,
        methods=["GET"],
        name="email_verify",
    ),
    Route(
        "/email-verify-resend/",
        endpoint=resend_email,
        methods=["GET", "POST", "OPTIONS"],
        name="email_verify_resend",
    ),
    # ...
    Route(
        "/reset-password/",
        endpoint=reset_password,
        methods=["GET", "POST"],
        name="reset_password",
    ),
    Route(
        "/reset-password-confirm/",
        endpoint=reset_password_confirm,
        methods=["GET", "POST"],
        name="reset_password_confirm",
    ),
]
