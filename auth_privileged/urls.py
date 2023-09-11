
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
        endpoint=prv_list,
        methods=["GET"],
        name="prv__list",
    ),
    Route(
        "/details/{id:int}",
        endpoint=prv_detail,
        methods=["GET"],
        name="prv__details",
    ),
    Route(
        "/update/{id:int}",
        endpoint=prv_update,
        methods=["GET", "POST", "OPTIONS"],
        name="prv__update",
    ),
    Route(
        "/login",
        endpoint=prv_login,
        methods=["GET", "POST", "OPTIONS"],
        name="prv__login",
    ),
    Route(
        "/logout",
        endpoint=prv_logout,
        methods=["GET", "POST", "OPTIONS"],
        name="prv__logout",
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
        prv_delete,
        methods=["GET", "POST"],
    ),
]
