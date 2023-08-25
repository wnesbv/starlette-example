
from pathlib import Path
from datetime import datetime, date

import random

from sqlalchemy import select, update as sqlalchemy_update, delete, func, true

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from account.models import User
from item.models import Item, Service, Rent

from options_select.opt_slc import all_total

from .opt_slc import in_admin, in_user, all_user, item_comment, in_item
from . import img


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def all_list(request):
    # ..
    template = "/admin/index.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            return templates.TemplateResponse(
                template, {"request": request,}
            )
        return PlainTextResponse(
            "You are banned - this is not your account..!"
        )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_list(request):
    # ..
    template = "/admin/item/list.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            stmt = await session.execute(select(Item).order_by(Item.created_at.desc()))
            obj_list = stmt.scalars().all()
            # ..
            obj_count = await all_total(session, Item)
            # ..
            context = {
                "request": request,
                "obj_list": obj_list,
                "obj_count": obj_count,
            }
            return templates.TemplateResponse(
                template, context
            )
        return PlainTextResponse(
            "You are banned - this is not your account..!"
        )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_details(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/item/details.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            cmt_list = await item_comment(session, id)
            # ..
            i = await in_item(session, id)
            # ..
            opt_service = await session.execute(
                select(Service)
                .where(Service.service_belongs==id)
            )
            all_service = opt_service.scalars().unique()
            # ..
            opt_rent = await session.execute(
                select(Rent)
                .join(Item.item_rent)
                .where(Rent.rent_belongs==id)
            )
            all_rent = opt_rent.scalars().unique()
            # ..
            context = {
                "request": request,
                "i": i,
                "cmt_list": cmt_list,
                "all_service": all_service,
                "all_rent": all_rent,
            }
            return templates.TemplateResponse(
                template, context
            )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_create(request):
    # ..
    mdl = "item"
    basewidth = 800
    template = "/admin/item/create.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            owner_all = await all_user(session)
            # ..
            if admin:
                return templates.TemplateResponse(
                    template, {
                        "request": request,
                        "owner_all": owner_all,
                    }
                )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            item_owner = form["item_owner"]
            # ..
            if file.filename == "":
                new = Item()
                new.title = title
                new.item_owner = item_owner
                new.description = description
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
                # ..
                return RedirectResponse(
                    f"/admin/item/details/{ new.id }",
                    status_code=302,
                )
            # ..
            id_fle = random.randint(100, 999)
            email = await in_user(session, item_owner)
            new = Item()
            new.title = title
            new.description = description
            new.id_fle = id_fle
            new.file = await img.img_creat(file, mdl, email.email, id_fle, basewidth)
            new.item_owner = item_owner
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/admin/item/details/{ new.id }",
                status_code=302,
            )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_update(request):
    # ..
    mdl = "item"
    basewidth = 800
    id = request.path_params["id"]
    template = "/admin/item/update.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        i = await in_item(session, id)
        # ..
        context = {
            "request": request,
            "i": i,
        }
        # ...
        if request.method == "GET":
            if admin and i:
                return templates.TemplateResponse(
                    template, context
                )
            return PlainTextResponse("False..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            del_obj = form.get("del_bool")
            # ..
            if file.filename == "":
                query = (
                    sqlalchemy_update(Item)
                    .where(Item.id == id)
                    .values(
                        title=title, description=description, file=i.file
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(query)
                await session.commit()

                if del_obj:
                    if Path(f".{i.file}").exists():
                        Path.unlink(f".{i.file}")

                    fle_not = (
                        sqlalchemy_update(Item)
                        .where(Item.id == id)
                        .values(file=None, modified_at=datetime.now())
                        .execution_options(synchronize_session="fetch")
                    )
                    await session.execute(fle_not)
                    await session.commit()
                    # ..
                    return RedirectResponse(
                        f"/admin/item/details/{id}",
                        status_code=302,
                    )
                return RedirectResponse(
                    f"/admin/item/details/{id}",
                    status_code=302,
                )
            # ..
            if i.id_fle is not None:
                id_fle = i.id_fle
            id_fle = random.randint(100, 999)
            email = await in_user(session, i.service_owner)
            file_query = (
                sqlalchemy_update(Item)
                .where(Item.id == id)
                .values(
                    title=title,
                    description=description,
                    file=await img.img_creat(file, mdl, email.email, id_fle, basewidth),
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/item/details/{id}",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_delete(request):
    # ..
    mdl = "item"
    id = request.path_params["id"]
    template = "/admin/item/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            i = await in_item(session, id)
            # ..
            if admin:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "i": i,
                    },
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            # ..
            i = await in_item(session, id)
            email = await in_user(session, i.item_owner)
            await img.id_fle_delete_tm(
                mdl, email.email, i.id_fle
            )
            # ..
            await session.delete(i)
            # ..
            await session.commit()
            # ..
            response = RedirectResponse(
                "/admin/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()
