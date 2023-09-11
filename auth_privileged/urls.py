
from starlette.routing import Route

from .views import (
    prv_list,
    prv_detail,
    prv_update,
    prv_login,
    prv_logout,
    prv_delete,
    verify_email,
    resend_email,
)

from .recovery import (
    reset_password,
    reset_password_confirm,
)


routes = [
    Route(
        "/list",
        prv_list,
        methods=["GET"],
    ),
    Route(
        "/details/{id:int}",
        prv_detail,
        methods=["GET"],
    ),
    Route(
        "/update/{id:int}",
        prv_update,
        methods=["GET", "POST", "OPTIONS"],
    ),
    Route(
        "/login",
        prv_login,
        methods=["GET", "POST", "OPTIONS"],
    ),
    Route(
        "/logout",
        prv_logout,
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
        prv_delete,
        methods=["GET", "POST"],
    ),
]
