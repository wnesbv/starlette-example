
from sqlalchemy import update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from account.opt_slc import auth

from options_select.opt_slc import for_in, id_and_owner

from auth_privileged.opt_slc import get_privileged_user

from .models import MessageGroup, OneChat


templates = Jinja2Templates(directory="templates")


@auth()
#...
async def all_chat(request):
    # ..
    template = "/chat/chat.html"
    # ..
    if request.method == "GET":
        async with async_session() as session:
            prv = await get_privileged_user(request, session)
            result = await for_in(session, OneChat)
        await engine.dispose()

        context = {
            "request": request,
            "result": result,
            "prv": prv,
        }
        return templates.TemplateResponse(template, context)


@auth()
#...
async def chat_update(request):
    # ..
    id = request.path_params["id"]
    id_group = request.path_params["id_group"]
    template = "/chat/update.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        context = {
            "request": request,
        }
        #...
        if request.method == "GET":
            if prv:
                i = await id_and_owner(session, MessageGroup, prv.id, id)
                context["i"] = i
                return templates.TemplateResponse(template, context)
            # ..
            if request.cookies.get("visited"):
                i = await id_and_owner(session, MessageGroup, request.user.user_id, id)
                context["i"] = i
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
                f"/chat/group/{ id_group }",
                status_code=302,
            )
            return response
    await engine.dispose()


@auth()
#...
async def chat_delete(request):

    id = request.path_params["id"]
    template = "/chat/delete.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        context = {
            "request": request,
        }
        #...
        if request.method == "GET":
            if prv:
                i = await id_and_owner(session, MessageGroup, prv.id, id)
                context["i"] = i
                return templates.TemplateResponse(template, context)
            # ..
            if request.cookies.get("visited"):
                i = await id_and_owner(session, MessageGroup, request.user.user_id, id)
                context["i"] = i
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("this is not your message..!")
        # ...
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
