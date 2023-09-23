
from sqlalchemy import update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from options_select.opt_slc import and_owner_request

from auth_privileged.opt_slc import (
    get_privileged_user,
    privileged,
    owner_prv,
    get_owner_prv,
    id_and_owner_prv,
)

from .models import MessageGroup, OneChat


templates = Jinja2Templates(directory="templates")


# ..
async def all_chat(request):
    # ..
    template = "/chat/chat.html"
    # ..
    if request.method == "GET":
        async with async_session() as session:
            prv = await get_privileged_user(request, session)
            stmt = await session.execute(select(OneChat))
            result = stmt.scalars().all()
        await engine.dispose()

        context = {
            "request": request,
            "result": result,
            "prv": prv,
        }
        return templates.TemplateResponse(template, context)

# ..
async def chat_update(request):
    # ..
    id = request.path_params["id"]
    template = "/chat/update.html"

    async with async_session() as session:
        #..
        detail = await and_owner_request(request, session, MessageGroup, id)
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
                sqlalchemy_update(MessageGroup)
                .where(MessageGroup.id == id)
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



# ..
async def chat_delete(request):

    id = request.path_params["id"]
    template = "/chat/delete.html"

    async with async_session() as session:
        # ..
        if request.method == "GET":
            detail = await and_owner_request(request, session, MessageGroup, id)
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
            query = delete(MessageGroup).where(MessageGroup.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response
    await engine.dispose()
