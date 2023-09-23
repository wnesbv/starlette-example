
import uvicorn

from sqlalchemy.future import select

from starlette.middleware import Middleware
from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from routes.urls import routes

from db_config.storage_config import engine, async_session
from db_config.settings import settings

from item.models import Slider

from account.models import User
from account.middleware import JwtBackend

from auth_privileged.opt_slc import get_privileged_user
from auth_privileged.middleware import PrivilegedBackend
from auth_privileged.auth import PrivilegedMiddleware


# ...
#from db_startup.db import on_app_startup
# ...


templates = Jinja2Templates(directory="templates")


middleware = [
    Middleware(
        PrivilegedMiddleware,
        backend=PrivilegedBackend(
            key=str(settings.SECRET_KEY),
            algorithm=settings.JWT_ALGORITHM,
        ),
    ),
    Middleware(
        AuthenticationMiddleware,
        backend=JwtBackend(
            key=str(settings.SECRET_KEY),
            algorithm=settings.JWT_ALGORITHM,
        ),
    ),
]


app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    # ...
    #on_startup=[on_app_startup],
    # on_shutdown=[on_app_shutdown],
    # ...
    middleware=middleware,
)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.route("/")
async def homepage(request):
    # ..
    template = "index.html"

    async with async_session() as session:
        stmt_sl = await session.execute(select(Slider))
        obj_sl = stmt_sl.scalars().all()
        obj = await get_privileged_user(request, session)
        # ..
        if not request.user.is_authenticated:
            context = {
                "request": request,
                "obj": obj,
                "obj_sl": obj_sl,
            }
            return templates.TemplateResponse(
                template, context
            )
        # ..
        stmt = await session.execute(
            select(User).where(User.id == request.user.user_id)
        )
        obj_list = stmt.scalars().all()
        # ..
        context = {
            "request": request,
            "obj_sl": obj_sl,
            "obj_list": obj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@app.route("/details/{id:int}")
async def details(request):
    # ..
    id = request.path_params["id"]
    template = "details.html"

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == id).where(User.id == request.user.user_id)
        )
        detail = result.scalars().first()
        context = {
            "request": request,
            "detail": detail,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@app.route("/error")
async def error(request):
    raise RuntimeError("Oh no")


@app.exception_handler(404)
async def not_found(request, exc):
    template = "404.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=404)


@app.exception_handler(500)
async def server_error(request, exc):
    template = "500.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=500)


@app.route("/messages")
def messages(request):
    template = "messages.html"
    msg = request.query_params["msg"]
    context = {
        "request": request,
        "msg": msg,
    }
    return templates.TemplateResponse(template, context)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
