
from sqlalchemy import update as sqlalchemy_update, delete

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from options_select.opt_slc import in_chat

from .models import MessageChat


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ..
async def chat_update(request):

    id = request.path_params["id"]
    template = "/chat/update.html"

    async with async_session() as session:
        #..
        detail = await in_chat(request, session, id)
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("this is not your message..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            message = form["message"]
            # ..
            query = (
                sqlalchemy_update(MessageChat)
                .where(MessageChat.id == id)
                .values(message=message)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/chat/group/{ detail.id_group }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ..
async def chat_delete(request):

    id = request.path_params["id"]
    template = "/chat/delete.html"

    async with async_session() as session:
        # ..
        if request.method == "GET":
            detail = await in_chat(request, session, id)
            if detail:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "detail": detail,
                    },
                )
            return PlainTextResponse("this is not your message..!")

        if request.method == "POST":
            # ..
            query = delete(MessageChat).where(MessageChat.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response
    await engine.dispose()
