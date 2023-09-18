from pathlib import Path
from datetime import datetime
import json

from sqlalchemy import update as sqlalchemy_update, delete

from sqlalchemy.future import select

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from json2html import json2html

from config.settings import BASE_DIR

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from item.models import ScheduleRent, ScheduleService
from options_select.opt_slc import for_id
from .opt_slc import (
    admin,
    get_admin_user,
    all_service,
    all_rent,
)


templates = Jinja2Templates(directory="templates")


@admin()
# ...
async def rent_list(request):
    # ..
    template = "/admin/schedule_rent/list.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            result = await session.execute(
                select(ScheduleRent).order_by(ScheduleRent.created_at)
            )
            obj_list = result.scalars().all()
            # ..
            context = {
                "request": request,
                "obj_list": obj_list,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@admin()
# ...
async def rent_details(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/schedule_rent/details.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            # ..
            if obj:
                i = await for_id(session, ScheduleRent, id)
                # ..
                obj_json = {
                    "id": i.id,
                    "title": i.title,
                    "start": i.start,
                    "end": i.end,
                }

                sch_json = json.dumps(obj_json, default=str)
                table_attributes = "style='width:100%', class='table table-bordered'"
                sch_json = json2html.convert(
                    json=sch_json, table_attributes=table_attributes
                )
                # ..
                context = {
                    "request": request,
                    "sch_json": sch_json,
                    "i": i,
                }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@admin()
# ...
async def rent_create(request):
    # ..
    template = "/admin/schedule_rent/create.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            prv = await get_admin_user(request, session)
            obj_rent = await all_rent(session)
            # ..
            if prv:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "obj_rent": obj_rent,
                    },
                )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            str_start = form["start"]
            str_end = form["end"]
            # ..
            title = form["title"]
            description = form["description"]
            sch_r_rent_id = form["sch_r_rent_id"]
            # ..
            start = datetime.strptime(str_start, settings.DATE_T)
            end = datetime.strptime(str_end, settings.DATE_T)
            # ..
            owner = prv.id
            # ...
            new = ScheduleRent()
            new.start = start
            new.end = end
            new.title = title
            new.description = description
            new.owner = owner
            new.sch_r_rent_id = int(sch_r_rent_id)
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/schedulerent/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@admin()
# ...
async def rent_update(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/schedulerent/update.html"

    async with async_session() as session:
        # ..
        prv = await get_admin_user(request, session)
        i = await for_id(session, ScheduleRent, id)
        # ..
        if request.method == "GET":
            if prv:
                context = {
                    "request": request,
                    "i": i,
                }
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            form = await request.form()
            # ..
            str_start = form["start"]
            str_end = form["end"]
            # ..
            title = form["title"]
            description = form["description"]
            # ..
            start = datetime.strptime(str_start, settings.DATE_T)
            end = datetime.strptime(str_end, settings.DATE_T)
            # ..
            query = (
                sqlalchemy_update(ScheduleRent)
                .where(ScheduleRent.id == id)
                .values(
                    start=start,
                    end=end,
                    title=title,
                    description=description,
                )
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/schedulerent/details/{ id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@admin()
# ...
async def rent_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/schedulerent/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            i = await for_id(session, ScheduleRent, id)
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
            query = delete(ScheduleRent).where(ScheduleRent.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/admin/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()


@admin()
# ...
async def delete_rent_csv(request):
    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            # ..
            if obj:
                directory = BASE_DIR / "static/service/"
                response = [
                    f.unlink() for f in Path(directory).glob("*") if f.is_file()
                ]
                response = RedirectResponse(
                    "/item/scheduleservice/list_service",
                    status_code=302,
                )
                return response
    await engine.dispose()
