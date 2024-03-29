
from pathlib import Path
from datetime import datetime

import json

from sqlalchemy import select, update as sqlalchemy_update, delete, func

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from account.models import User

from db_config.storage_config import engine, async_session
from options_select.opt_slc import all_total, for_id, for_in

from item.models import Item, Rent, ScheduleRent
from .opt_slc import (
    admin,
    get_admin_user,
    rent_comment,
)
from . import img


templates = Jinja2Templates(directory="templates")


@admin()
# ...
async def i_list(request):
    # ..
    template = "/admin/rent/list.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            # ..
            stmt = await session.execute(select(Rent).order_by(Rent.created_at.desc()))
            obj_list = stmt.scalars().all()
            # ..
            obj_count = await all_total(session, Rent)
            # ..
            context = {
                "request": request,
                "obj_list": obj_list,
                "obj_count": obj_count,
            }
            return templates.TemplateResponse(template, context)
        return PlainTextResponse("You are banned - this is not your account..!")
    await engine.dispose()


@admin()
# ...
async def i_details(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/rent/details.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            # ..
            cmt_list = await rent_comment(session, id)
            # ..
            i = await for_id(session, Rent, id)
            # ..
            stmt = await session.execute(
                select(ScheduleRent)
                .where(ScheduleRent.sch_r_rent_id == id)
                .order_by(ScheduleRent.id.desc())
            )
            obj_list = stmt.scalars().all()
            # ..
            obj = [
                {
                    "start": i.start,
                    "end": i.end,
                    "title": i.title,
                }
                for i in obj_list
            ]
            sch_json = json.dumps(obj, default=str)
            # ..
            context = {
                "request": request,
                "i": i,
                "cmt_list": cmt_list,
                "obj_list": obj_list,
                "sch_json": sch_json,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@admin()
# ...
async def i_create(request):
    # ..
    basewidth = 800
    template = "/admin/rent/create.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            owner_all = await for_in(session, User)
            obj_item = await for_in(session, Item)
            # ..
            if obj:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "owner_all": owner_all,
                        "obj_item": obj_item,
                    },
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
            rent_belongs = form["rent_belongs"]
            # ..
            if file.filename == "":
                new = Rent()
                new.title = title
                new.description = description
                new.owner = owner
                new.rent_belongs = int(rent_belongs)
                # ..
                session.add(new)
                await session.commit()
                # ..
                return RedirectResponse(
                    f"/item/rent/details/{ new.id }",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, owner)
            # ..
            new = Rent()
            new.title = title
            new.description = description
            new.owner = int(owner)
            new.rent_belongs = int(rent_belongs)
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.flush()
            new.file = await img.rent_img_creat(
                file, email.email, rent_belongs, new.id, basewidth
            )
            session.add(new)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/item/rent/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@admin()
# ...
async def i_update(request):
    # ..
    basewidth = 800
    id = request.path_params["id"]
    template = "/item/rent/update.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        i = await for_id(session, Rent, id)
        # ..
        context = {
            "request": request,
            "i": i,
        }
        # ...
        if request.method == "GET":
            if obj:
                return templates.TemplateResponse(template, context)
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
                    sqlalchemy_update(Rent)
                    .where(Rent.id == id)
                    .values(
                        title=title,
                        description=description,
                        file=i.file,
                        modified_at=datetime.now(),
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(query)
                await session.commit()

                if del_obj:
                    if Path(f".{i.file}").exists():
                        Path.unlink(f".{i.file}")

                    fle_not = (
                        sqlalchemy_update(Rent)
                        .where(Rent.id == id)
                        .values(file=None, modified_at=datetime.now())
                        .execution_options(synchronize_session="fetch")
                    )
                    await session.execute(fle_not)
                    await session.commit()
                    return RedirectResponse(
                        f"/item/rent/details/{id}",
                        status_code=302,
                    )
                return RedirectResponse(
                    f"/item/rent/details/{id}",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, i.owner)
            file_query = (
                sqlalchemy_update(Rent)
                .where(Rent.id == id)
                .values(
                    title=title,
                    description=description,
                    file=await img.rent_img_creat(
                        file, email.email, i.rent_belongs, i.id, basewidth
                    ),
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/item/rent/details/{id}",
                status_code=302,
            )
            return response
    await engine.dispose()


@admin()
# ...
async def i_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/rent/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            i = await for_id(session, Rent, id)
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
            i = await for_id(session, Rent, id)
            email = await for_id(session, User, i.owner)
            # ..
            await img.del_rent(email.email, i.rent_belongs, id)
            # ..
            await session.delete(i)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()
