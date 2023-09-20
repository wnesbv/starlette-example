
from sqlalchemy import select, insert, update as sqlalchemy_update, delete

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from options_select.opt_slc import for_id, and_owner_request, in_user_accepted

from auth_privileged.opt_slc import (
    get_privileged_user,
    privileged,
    owner_prv,
    get_owner_prv,
    id_and_owner_prv,
)
from account.views import auth

from .models import MessageChat, GroupChat
from .opt_slc import in_obj_participant, in_obj_accepted


templates = Jinja2Templates(directory="templates")


async def group_list(request):
    # ..
    template = "/group/list.html"

    async with async_session() as session:
        result = await session.execute(select(GroupChat).order_by(GroupChat.id))
        obj_list = result.scalars().all()
        context = {
            "request": request,
            "obj_list": obj_list,
        }

        return templates.TemplateResponse(template, context)
    await engine.dispose()

@auth()
# ..request.auth.scopes
async def group_details(request):
    # ..
    id = request.path_params["id"]
    id_group = request.path_params["id"]
    template = "/group/details.html"

    if request.method == "GET":
        async with async_session() as session:
            # ..
            i = await for_id(session, GroupChat, id)
            prv = await get_privileged_user(request, session)
            stmt_chat = await session.execute(
                select(MessageChat).where(MessageChat.id_group == id)
            )
            group_chat = stmt_chat.scalars().all()
            # ..
            context = {
                "request": request,
                "i": i,
                "prv": prv,
                "id_group": id_group,
                "group_chat": group_chat,
            }
            # ..
            if prv:
                for_prv = await in_obj_participant(
                    session, prv.id, id
                )
                for_prv_accepted = await in_obj_accepted(
                    session, prv.id, id
                )
                # ..
                context["for_prv"] = for_prv
                context["for_prv_accepted"] = for_prv_accepted
            # ..
            if request.cookies.get("visited"):
                for_user = await in_obj_participant(
                    session, request.user.user_id, id
                )
                for_user_accepted = await in_obj_accepted(
                    session, request.user.user_id, id
                )
                # ..
                context["for_user"] = for_user
                context["for_user_accepted"] = for_user_accepted

            return templates.TemplateResponse(template, context)
        await engine.dispose()


# ..
async def group_create(request):
    # ..
    template = "/group/create.html"

    async with async_session() as session:
        # ...
        if request.method == "GET":
            return templates.TemplateResponse(
                template,
                {
                    "request": request,
                },
            )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            owner = request.user.user_id
            # ..
            new = GroupChat()
            new.title = title
            new.owner = owner
            new.description = description

            session.add(new)
            await session.commit()
            # ..
            query = insert(MessageChat).values(
                owner=owner,
                id_group=new.id,
                message=f"New message admin group-{owner}..!",
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/chat/group/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


# ..
async def group_update(request):
    # ..
    id = request.path_params["id"]
    template = "/group/update.html"

    async with async_session() as session:
        # ..
        detail = await and_owner_request(request, session, GroupChat, id)
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            detail.title = form["title"]
            detail.description = form["description"]
            # ..
            query = (
                sqlalchemy_update(GroupChat)
                .where(GroupChat.id == id)
                .values(form)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/chat/group/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


# ..
async def group_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/group/delete.html"

    async with async_session() as session:
        # ...
        if request.method == "GET":
            # ..
            detail = await and_owner_request(request, session, GroupChat, id)
            if detail:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "detail": detail,
                    },
                )
            return PlainTextResponse("this is not your group..!")
        # ...
        if request.method == "POST":
            # ..
            query = delete(GroupChat).where(GroupChat.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response
    await engine.dispose()
