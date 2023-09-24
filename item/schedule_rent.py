from datetime import datetime

import json

from sqlalchemy import update as sqlalchemy_update, delete, and_

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from json2html import json2html

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from mail.send import send_mail

from auth_privileged.opt_slc import (
    privileged,
    get_owner_prv,
    id_and_owner_prv,
)

from .create_update import child_create, child_update
from .models import Rent, ScheduleRent


templates = Jinja2Templates(directory="templates")


@privileged()
# ...
async def list_rent(request):
    # ..
    template = "/schedulerent/list.html"

    async with async_session() as session:
        # ..
        obj_list = await get_owner_prv(request, session, ScheduleRent)
        # ..
        context = {
            "request": request,
            "obj_list": obj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@privileged()
# ...
async def details_rent(request):
    # ..
    id = request.path_params["id"]
    template = "/schedulerent/details.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await id_and_owner_prv(request, session, ScheduleRent, id)
            if i:
                # ..
                obj_list = await get_owner_prv(request, session, ScheduleRent)
                # ..
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
                    json=sch_json, table_attributes=table_attributes
                )
                context = {
                    "request": request,
                    "sch_json": sch_json,
                    "i": i,
                }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@privileged()
# ...
async def create_rent(request):
    context = {}
    # ..
    form = await request.form()
    start = form.get("start")
    end = form.get("end")
    sch_r_rent_id = form.get("sch_r_rent_id")
    # ..
    new = ScheduleRent()
    new.sch_r_rent_id = sch_r_rent_id
    # ..
    if start and end is not None:
        new.start = datetime.strptime(start, settings.DATE_T)
        new.end = datetime.strptime(end, settings.DATE_T)
    # ..
    obj = await child_create(request, context, form, Rent, new, "schedulerent", "rent")
    return obj


@privileged()
# ...
async def update_rent(request):
    # ..
    id = request.path_params["id"]
    # ..
    context = {}
    # ..
    form = await request.form()
    # ..
    start = form.get("start")
    end = form.get("end")
    title = form.get("title")
    description = form.get("description")
    # ..
    if start and end is not None:
        form = {
        "start": datetime.strptime(start, settings.DATE_T),
        "end": datetime.strptime(end, settings.DATE_T),
        "title": title,
        "description": description,
        }
        # ..
    obj = await child_update(request, context, ScheduleRent, id, form, "schedulerent")
    return obj


@privileged()
# ...
async def schedule_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/schedulerent/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await id_and_owner_prv(request, session, ScheduleRent, id)
            if i:
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
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/schedulerent/list",
                status_code=302,
            )
            return response
    await engine.dispose()
