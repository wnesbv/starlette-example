
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
        user_register,
        methods=["GET", "POST", "OPTIONS"],
    ),
    Route(
        "/list",
        user_list,
        methods=["GET"],
    ),
    Route(
        "/details/{id:int}",
        user_detail,
        methods=["GET"],
    ),
    Route(
        "/update/{id:int}",
        user_update,
        methods=["GET", "POST", "OPTIONS"],
    ),
    Route(
        "/login",
        user_login,
        methods=["GET", "POST", "OPTIONS"],
        name="user_to_login",
    ),
    Route(
        "/logout",
        user_logout,
        methods=["GET", "POST", "OPTIONS"],
    ),
    # ...
    Route(
        "/email-verify/",
        verify_email,
        methods=["GET"],
    ),
    Route(
        "/email-verify-resend/",
        resend_email,
        methods=["GET", "POST", "OPTIONS"],
    ),
    # ...
    Route(
        "/reset-password/",
        reset_password,
        methods=["GET", "POST"],
    ),
    Route(
        "/reset-password-confirm/",
        reset_password_confirm,
        methods=["GET", "POST"],
    ),
    Route(
        "/delete/{id:int}",
        user_delete,
        methods=["GET", "POST"],
    ),
]
