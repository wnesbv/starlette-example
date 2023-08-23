
from starlette.routing import Route

from .views import (
    user_list,
    user_detail,
    user_update,
    user_login,
    user_register,
    user_logout,
    verify_email,
    resend_email,
    user_delete,
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
        "/list",
        endpoint=user_list,
        methods=["GET"],
        name="user__list",
    ),
    Route(
        "/details/{id:int}",
        endpoint=user_detail,
        methods=["GET"],
        name="user__details",
    ),
    Route(
        "/update/{id:int}",
        endpoint=user_update,
        methods=["GET", "POST", "OPTIONS"],
        name="user__update",
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
    Route(
        "/delete/{id:int}",
        user_delete,
        methods=["GET", "POST"],
    ),
]
