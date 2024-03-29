
from pathlib import Path
from datetime import datetime

from sqlalchemy import select, update as sqlalchemy_update, delete, func, true

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from account.models import User
from item.models import Item, Service, Rent

from options_select.opt_slc import all_total, for_id, for_in

from .opt_slc import admin, get_admin_user, item_comment
from . import img


templates = Jinja2Templates(directory="templates")


@admin()
# ...
async def all_list(request):
    # ..
    template = "/admin/index.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            return templates.TemplateResponse(
                template, {"request": request,}
            )
        return PlainTextResponse(
            "You are banned - this is not your account..!"
        )
    await engine.dispose()


@admin()
# ...
async def i_list(request):
    # ..
    template = "/admin/item/list.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
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


@admin()
# ...
async def i_details(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/item/details.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            # ..
            cmt_list = await item_comment(session, id)
            # ..
            i = await for_id(session, Item, id)
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


@admin()
# ...
async def i_create(request):
    # ..
    basewidth = 800
    template = "/admin/item/create.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            owner_all = await for_in(session, User)
            # ..
            if obj:
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
            owner = form["owner"]
            # ..
            if file.filename == "":
                new = Item()
                new.title = title
                new.owner = owner
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
            email = await for_id(session, User, owner)
            new = Item()
            new.title = title
            new.description = description
            new.owner = owner
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.flush()
            print(" new id..", new.id)
            new.file = await img.item_img_creat(
                file, email.email, new.id, basewidth
            )
            session.add(new)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/admin/item/details/{ new.id }",
                status_code=302,
            )
    await engine.dispose()


@admin()
# ...
async def i_update(request):
    # ..
    basewidth = 800
    id = request.path_params["id"]
    template = "/admin/item/update.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        i = await for_id(session, Item, id)
        # ..
        context = {
            "request": request,
            "i": i,
        }
        # ...
        if request.method == "GET":
            if obj and i:
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
                        title=title, description=description, file=i.file, modified_at=datetime.now(),
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
            email = await for_id(session, User, i.owner)
            file_query = (
                sqlalchemy_update(Item)
                .where(Item.id == id)
                .values(
                    title=title,
                    description=description,
                    file=await img.item_img_creat(file, email.email, id, basewidth),
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


@admin()
# ...
async def i_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/item/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            i = await for_id(session, Item, id)
            # ..
            if obj:
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
            i = await for_id(session, Item, id)
            email = await for_id(session, User, i.owner)
            await img.del_tm(email.email, i.id)
            # ..
            await session.delete(i)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/admin/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()
