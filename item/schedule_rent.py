
from pathlib import Path

from datetime import datetime

import json

from sqlalchemy import(
    update as sqlalchemy_update,
    delete,
    and_
)
from sqlalchemy.future import select

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from json2html import json2html

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from mail.send import send_mail

from options_select.opt_slc import(
    user_rt,
    schedule_rent,
    in_schedule_rent,
    details_schedule_rent
)

from .models import ScheduleRent


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def list_rent(
    request
):
    template = "/item/schedule/list_rent.html"
    async with async_session() as session:
        #..
        odj_list = await schedule_rent(request, session)
        #..
        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(
            template, context
        )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def details_rent(
    request
):
    template = "/item/schedule/details_rent.html"
    async with async_session() as session:

        if request.method == "GET":
            #..
            sch = await in_schedule_rent(request, session)
            if sch:
                #..
                obj_list = await details_schedule_rent(request, session)
                #..
                obj = [
                    {
                        "id": to.id,
                        "title": to.title,
                        "start": to.start,
                        "end": to.end,
                    }
                    for to in obj_list
                ]
                sch_json = json.dumps(obj, default=str)
                table_attributes = "style='width:100%', class='table table-bordered'"
                sch_json = json2html.convert(
                    json = sch_json,
                    table_attributes=table_attributes
                )
                context = {
                    "request": request,
                    "sch_json": sch_json,
                    "sch": sch,
                }
            return templates.TemplateResponse(
                template, context
            )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def create_rent(
    request
):
    template = "/item/schedule/create_rent.html"
    async with async_session() as session:

        if request.method == "GET":
            #..
            odj_rent = await user_rt(request, session)
            #..
            return templates.TemplateResponse(
                template, {
                    "request": request,
                    "odj_rent": odj_rent,
                }
            )
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            str_start = form["start"]
            str_end = form["end"]
            #..
            title = form["title"]
            description = form["description"]
            sch_r_rent_id = form["sch_r_rent_id"]
            #..
            start = datetime.strptime(
                str_start, settings.DATE_T
            )
            end = datetime.strptime(
                str_end, settings.DATE_T
            )
            #..
            sch_r_owner = request.user.user_id
            #...
            new = ScheduleRent()
            new.start = start
            new.end = end
            new.title = title
            new.description = description
            new.sch_r_owner = sch_r_owner
            new.sch_r_rent_id = int(sch_r_rent_id)
            new.created_at = datetime.now()
            #..
            session.add(new)
            session.refresh(new)
            await session.commit()
            #..
            await send_mail(
                f"A new object has been created - {new}: {title}"
            )
            #..
            response = RedirectResponse(
                f"/item/schedule-rent/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def update_rent(
    request
):
    id = request.path_params["id"]
    template = "/item/schedule/update_rent.html"

    async with async_session() as session:
        #..
        detail = await in_schedule_rent(request, session)
        #..
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail:
                return templates.TemplateResponse(
                    template, context
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            form = await request.form()
            #..
            str_start = form["start"]
            str_end = form["end"]
            #..
            title = form["title"]
            description = form["description"]
            #..
            start = datetime.strptime(
                str_start, settings.DATE_T
            )
            end = datetime.strptime(
                str_end, settings.DATE_T
            )
            #..
            query = (
                sqlalchemy_update(ScheduleRent)
                .where(ScheduleRent.id==id)
                .values(
                    start=start,
                    end=end,
                    title=title,
                    description=description,
                )
                .execution_options(synchronize_session="fetch")
            )
            #..
            await session.execute(query)
            await session.commit()
            #..
            await send_mail(
                f"changes were made at the facility - {detail}: {detail.title}"
            )
            #..
            response = RedirectResponse(
                f"/item/schedule-rent/details/{detail.id}",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def delete(
    request
):
    id = request.path_params["id"]
    template = "/item/schedule/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            detail = await in_schedule_rent(request, session)
            if detail:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "detail": detail,
                    },
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            #..
            query = (
                delete(ScheduleRent)
                .where(ScheduleRent.id == id)
            )
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/item/schedule-rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()
