from datetime import datetime

import json

from sqlalchemy import update as sqlalchemy_update, delete, and_
from sqlalchemy.future import select

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from json2html import json2html

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from mail.send import send_mail

from options_select.opt_slc import (
    for_id,
    all_total,
)

from auth_privileged.opt_slc import (
    privileged,
    get_owner_prv,
    id_and_owner_prv,
    get_privileged_user,
    sch_sv_service_owner_id,
)

from .create_update import child_create, child_update
from .models import Service, ScheduleService, MyEnum


templates = Jinja2Templates(directory="templates")


@privileged()
# ...
async def list_service(request):
    # ..
    template = "/scheduleservice/list_service.html"

    async with async_session() as session:
        # ..
        obj_count = await all_total(session, Service)
        prv = await get_privileged_user(request, session)
        stmt = await session.execute(
            select(Service)
            .join(ScheduleService.sch_s_service)
            .where(ScheduleService.owner == prv.id)
            .order_by(ScheduleService.id.desc())
        )
        obj_list = stmt.scalars().unique()
        # ..
        context = {
            "request": request,
            "obj_list": obj_list,
            "obj_count": obj_count,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@privileged()
# ...
async def list_service_id(request):
    # ..
    id = request.path_params["id"]
    template = "/scheduleservice/list_service_id.html"

    async with async_session() as session:
        # ..
        obj_list = await sch_sv_service_owner_id(request, session, id)
        # ..
        context = {
            "request": request,
            "obj_list": obj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@privileged()
# ...
async def details_service(request):
    # ..
    id = request.path_params["id"]
    service = request.path_params["service"]
    template = "/scheduleservice/details_service.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await id_and_owner_prv(request, session, ScheduleService, id)
            if i:
                # ..
                obj_list = sch_sv_service_owner_id(request, session, service)
                # ..
                obj = [
                    {
                        "id": i.id,
                        "name": i.name,
                        "type_on": i.type_on,
                        "title": i.title,
                        "number_on": i.number_on,
                        "there_is": i.there_is,
                        "description": i.description,
                    }
                    for i in obj_list
                ]
                sch_json = json.dumps(obj, default=str)
                # ..
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


@privileged()
# ...
async def details(request):
    # ..
    id = request.path_params["id"]
    template = "/scheduleservice/details.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await id_and_owner_prv(request, session, ScheduleService, id)
            if obj:
                # ..
                i = await for_id(session, ScheduleService, id)
                # ..
                context = {
                    "request": request,
                    "i": i,
                }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@privileged()
# ...
async def create_service(request):
    # ..
    objects = list(MyEnum)
    context = {
        "objects": objects,
    }
    # ..
    form = await request.form()
    # ..
    str_number = form.get("number_on")
    str_there = form.get("there_is")
    name = form.get("name")
    type_on = form.get("type_on")
    sch_s_service_id = form.get("sch_s_service_id")
    # ..
    new = ScheduleService()
    new.name = name
    new.type_on = type_on
    new.sch_s_service_id = sch_s_service_id
    # ..
    if str_number and str_there is not None:
        new.number_on = datetime.strptime(str_number, settings.DATE)
        new.there_is = datetime.strptime(str_there, settings.DATE_T)
    # ..
    obj = await child_create(
        request, context, form, Service, new, "scheduleservice", "service"
    )
    return obj


@privileged()
# ...
async def update_service(request):
    # ..
    id = request.path_params["id"]
    # ..
    context = {}
    # ..
    form = await request.form()
    # ..
    number_on = form.get("number_on")
    there_is = form.get("there_is")
    title = form.get("title")
    description = form.get("description")
    type_on = form.get("type_on")
    # ..
    if number_on and there_is is not None:
        form = {
            "number_on": datetime.strptime(number_on, settings.DATE_T),
            "there_is": datetime.strptime(there_is, settings.DATE_T),
            "title": title,
            "description": description,
            "type_on": type_on,
        }
        # ..
    obj = await child_update(
        request, context, ScheduleService, id, form, "scheduleservice"
    )
    return obj


@privileged()
# ...
async def schedule_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/scheduleservice/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await id_and_owner_prv(request, session, ScheduleService, id)
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
            query = delete(ScheduleService).where(ScheduleService.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/scheduleservice/list",
                status_code=302,
            )
            return response
    await engine.dispose()
