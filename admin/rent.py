
import json

from sqlalchemy import select, update as sqlalchemy_update, delete, func

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from item.models import Rent, ScheduleRent
from .opt_slc import (
    all_item,
    in_admin,
    rent_comment,
    in_rent,
)

templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def item_list(request):

    template = "/admin/rent/list.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            stmt = await session.execute(select(Rent).order_by(Rent.created_at.desc()))
            odj_list = stmt.scalars().all()
            # ..
            stmt = await session.execute(select(func.count(Rent.id)))
            odj_count = stmt.scalars().all()
            # ..
            context = {
                "request": request,
                "odj_list": odj_list,
                "odj_count": odj_count,
            }
            return templates.TemplateResponse(template, context)
        return PlainTextResponse("You are banned - this is not your account..!")
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_details(request):

    id = request.path_params["id"]
    template = "/admin/rent/details.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            cmt_list = await rent_comment(session, id)
            # ..
            detail = await in_rent(session, id)
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
                "detail": detail,
                "cmt_list": cmt_list,
                "obj_list": obj_list,
                "sch_json": sch_json,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_create(request):

    template = "/item/rent/create.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            odj_item = await all_item(session)
            # ..
            if admin:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "odj_item": odj_item,
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
            rent_belongs = form["rent_belongs"]
            # ..
            rent_owner = request.user.user_id
            # ..
            new = Rent()
            new.title = title
            new.description = description
            new.file = file
            new.rent_owner = rent_owner
            # ..
            new.rent_belongs = int(rent_belongs)
            # ..
            session.add(new)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/item/rent/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_update(request):

    id = request.path_params["id"]
    template = "/item/rent/update.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        detail = await in_rent(session, id)
        # ..
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if admin:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            # ..
            file_query = (
                sqlalchemy_update(Rent)
                .where(Rent.id == id)
                .values(
                    file=file,
                    title=title,
                    description=description
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/item/rent/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_delete(request):

    id = request.path_params["id"]
    template = "/item/rent/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            detail = await in_rent(session, id)
            # ..
            if admin:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "detail": detail,
                    },
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            query = delete(Rent).where(Rent.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()
