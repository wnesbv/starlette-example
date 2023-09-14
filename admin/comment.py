
from datetime import datetime

import json

from sqlalchemy import (
    select,
    update as sqlalchemy_update,
    delete,
    func,
    asc,
    desc,
    and_,
    true,
)

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from comment.models import Comment
from account.models import User

from options_select.opt_slc import for_id
from .opt_slc import admin, all_user, get_admin_user


templates = Jinja2Templates(directory="templates")


async def cmt_child_create(request, new, id, item):
    # ..
    template = "/admin/comment/create.html"

    async with async_session() as session:
        # ..
        owner_all = await all_user(session)
        # ..
        obj = await get_admin_user(request, session)
        # ...
        if request.method == "GET":
            if obj:
                context = {
                    "request": request,
                    "owner_all": owner_all,
                }
                return templates.TemplateResponse(
                    template, context
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            opinion = form["opinion"]
            owner = form["owner"]
            # ..
            new.opinion = opinion
            new.owner = int(owner)
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.flush()
            i = await for_id(session, User, new.owner)
            new.user_on = {"name": i.name, "email": i.email}
            session.add(new)
            await session.commit()
            print("new", new)
            # ..
            response = RedirectResponse(
                f"/admin/{item}/details/{ id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@admin()
# ...
async def cmt_item_create(request):
    # ..
    id = request.path_params["id"]
    # ..
    new = Comment()
    new.cmt_item_id = id
    # ..
    obj = await cmt_child_create(
        request, new, id, "item"
    )
    return obj


@admin()
# ...
async def cmt_rent_create(request):
    # ..
    id = request.path_params["id"]
    # ..
    new = Comment()
    new.cmt_rent_id = id
    # ..
    obj = await cmt_child_create(
        request, new, id, "rent"
    )
    return obj


@admin()
# ...
async def cmt_service_create(request):
    # ..
    id = request.path_params["id"]
    # ..
    new = Comment()
    new.cmt_service_id = id
    # ..
    obj = await cmt_child_create(
        request, new, id, "service"
    )
    return obj


async def cmt_child_update(request, id, cmt_i_id, item):
    # ..
    template = "/admin/comment/update.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        i = await for_id(session, Comment, id)
        # ..
        if request.method == "GET":
            if obj and i:
                context = {
                    "request": request,
                    "i": i,
                }
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            opinion = form["opinion"]
            # ..
            query = (
                sqlalchemy_update(Comment)
                .where(Comment.id == id)
                .values(opinion=opinion, modified_at=datetime.now())
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/{item}/details/{ cmt_i_id }",
                status_code=302,
            )
    await engine.dispose()


@admin()
# ...
async def cmt_item_update(request):
    # ..
    id = request.path_params["id"]
    async with async_session() as session:
        i = await for_id(session, Comment, id)
        obj = await cmt_child_update(
            request, id, i.cmt_item_id, "item"
        )
        return obj
    await engine.dispose()


@admin()
# ...
async def cmt_rent_update(request):
    # ..
    id = request.path_params["id"]
    async with async_session() as session:
        i = await for_id(session, Comment, id)
        obj = await cmt_child_update(
            request, id, i.cmt_rent_id, "rent"
        )
        return obj
    await engine.dispose()


@admin()
# ...
async def cmt_service_update(request):
    # ..
    id = request.path_params["id"]
    async with async_session() as session:
        i = await for_id(session, Comment, id)
        obj = await cmt_child_update(
            request, id, i.cmt_service_id, "service"
        )
        return obj
    await engine.dispose()


@admin()
# ...
async def cmt_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/comment/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            i = await for_id(session, Comment, id)
            # ..
            if obj:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "i": i,
                    },
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            query = delete(Comment).where(Comment.id == id)
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()
