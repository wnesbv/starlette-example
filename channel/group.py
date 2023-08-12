
from sqlalchemy import select, insert, update as sqlalchemy_update, delete

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from options_select.opt_slc import in_group_chat

from .models import MessageChat, GroupChat


templates = Jinja2Templates(directory="templates")


async def group_list(request):

    template = "/group/list.html"

    async with async_session() as session:

        result = await session.execute(
            select(GroupChat)
            .order_by(GroupChat.id)
        )
        odj_list = result.scalars().all()
        context = {
            "request": request,
            "odj_list": odj_list,
        }

        return templates.TemplateResponse(template, context)
    await engine.dispose()


# ..
@requires("authenticated", redirect="user_login")
# ..
async def group_details(request):

    if request.method == "GET":
        
        id = request.path_params["id"]
        id_group = request.path_params["id"]
        template = "/group/details.html"

        async with async_session() as session:
            # ..
            stmt = await session.execute(
                select(GroupChat)
                .where(GroupChat.id == id)
            )
            detail = stmt.scalars().first()
            # ..
            stmt_chat = await session.execute(
                select(MessageChat)
                .where(
                    MessageChat.id_group == id
                )
            )
            group_chat = stmt_chat.scalars()
            context = {
                "request": request,
                "detail": detail,
                "id_group": id_group,
                "group_chat": group_chat,
            }

            return templates.TemplateResponse(template, context)
        await engine.dispose()


@requires("authenticated", redirect="user_login")
# ..
async def group_create(request):

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
            admin_group = request.user.user_id
            # ..
            new = GroupChat()
            new.title = title
            new.admin_group = admin_group
            new.description = description

            session.add(new)
            session.refresh(new)
            await session.commit()
            # ..
            query = insert(MessageChat).values(
                owner_chat=admin_group,
                id_group=new.id,
                message=f"New message admin group-{admin_group}..!",
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


@requires("authenticated", redirect="user_login")
# ..
async def group_update(request):

    id = request.path_params["id"]
    template = "/group/update.html"

    async with async_session() as session:
        # ..
        detail = await in_group_chat(request, session, id)
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


@requires("authenticated", redirect="user_login")
# ..
async def group_delete(request):

    id = request.path_params["id"]
    template = "/group/delete.html"

    async with async_session() as session:
        # ...
        if request.method == "GET":
            #..
            detail = await in_group_chat(request, session, id)
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
            query = (
                delete(GroupChat)
                .where(GroupChat.id == id)
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response
    await engine.dispose()
