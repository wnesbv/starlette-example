
from sqlalchemy import select, insert, update as sqlalchemy_update, delete

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from account.opt_slc import auth

from auth_privileged.opt_slc import get_privileged_user

from options_select.opt_slc import id_and_owner

from .models import OneOneChat
from .opt_slc import one_one_select, one_one_group


templates = Jinja2Templates(directory="templates")


@auth()
#...
async def one_one_details(request):
    # ..
    ref_num = request.path_params["ref_num"]
    template = "/one_one/details.html"

    if request.method == "GET":
        async with async_session() as session:
            # ..
            prv = await get_privileged_user(request, session)
            # ..
            context = {
                "request": request,
                "prv": prv,
                "ref_num": ref_num,
            }
            # ..
            if prv:
                user = await one_one_select(session, ref_num, prv.id)
                if user:
                    obj_list = await one_one_group(session, ref_num)
                    # ..
                    context["user"] = user
                    context["obj_list"] = obj_list
                    return templates.TemplateResponse(template, context)
                return RedirectResponse("/")
            # ..
            if request.cookies.get("visited"):
                user = await one_one_select(session, ref_num, request.user.user_id)
                if user:
                    obj_list = await one_one_group(session, ref_num)
                    # ..
                    context["user"] = user
                    context["obj_list"] = obj_list
                    return templates.TemplateResponse(template, context)
                return RedirectResponse("/")
        await engine.dispose()


@auth()
#...
async def one_one_update(request):
    # ..
    id = request.path_params["id"]
    ref_num = request.path_params["ref_num"]
    template = "/one_one/update.html"

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
                i = await id_and_owner(session, OneOneChat, prv.id, id)
                context["i"] = i
                return templates.TemplateResponse(template, context)
            # ..
            if request.cookies.get("visited"):
                i = await id_and_owner(session, OneOneChat, request.user.user_id, id)
                context["i"] = i
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("this is not your message..!")
        #...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            message = form["message"]
            # ..
            query = (
                sqlalchemy_update(OneOneChat)
                .where(OneOneChat.id == id)
                .values(message=message)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/chat/user/{ ref_num }",
                status_code=302,
            )
            return response
    await engine.dispose()


@auth()
# ..
async def one_one_delete(request):

    id = request.path_params["id"]
    template = "/one_one/delete.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        context = {
            "request": request,
        }
        # ..
        if request.method == "GET":
            if prv:
                i = await id_and_owner(session, OneOneChat, prv.id, id)
                context["i"] = i
                return templates.TemplateResponse(template, context)
            # ..
            if request.cookies.get("visited"):
                i = await id_and_owner(session, OneOneChat, request.user.user_id, id)
                context["i"] = i
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("this is not your message..!")

        if request.method == "POST":
            # ..
            query = delete(OneOneChat).where(OneOneChat.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/",
                status_code=302,
            )
            return response
    await engine.dispose()
