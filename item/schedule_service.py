
from pathlib import Path

from datetime import datetime

import json

from sqlalchemy import update as sqlalchemy_update, delete

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from json2html import json2html

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from mail.send import send_mail

from options_select.opt_slc import (
    user_sv,
    schedule_srv,
    in_schedule_service,
    schedule_service_id,
    details_schedule_service,
)

from .models import ScheduleService


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def list_service_id(request):
    template = "/schedule/list_service_id.html"
    async with async_session() as session:
        # ..
        odj_list = await schedule_service_id(request, session)
        # ..
        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def list_service(request):

    id = request.path_params["id"]
    template = "/schedule/list_service.html"

    async with async_session() as session:
        # ..
        odj_list = await schedule_srv(request, session, id)
        # ..
        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def details_service(request):

    id = request.path_params["id"]
    service = request.path_params["service"]
    template = "/schedule/details_service.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            sch = await in_schedule_service(request, session, id)
            if sch:
                # ..
                obj_list = await details_schedule_service(request, session, service)
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
                #..
                table_attributes = "style='width:100%', class='table table-bordered'"
                sch_json = json2html.convert(
                    json=sch_json,
                    table_attributes=table_attributes
                )
                # ..
                context = {
                    "request": request,
                    "sch_json": sch_json,
                    "sch": sch,
                }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def create_service(request):
    template = "/schedule/create_service.html"
    async with async_session() as session:

        if request.method == "GET":
            # ..
            odj_service = await user_sv(request, session)
            # ..
            return templates.TemplateResponse(
                template,
                {
                    "request": request,
                    "odj_service": odj_service,
                },
            )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            str_date = form["number_on"]
            str_there_is = form["there_is"]
            # ..
            name = form["name"]
            type_on = form["type_on"]
            title = form["title"]
            description = form["description"]
            sch_s_service_id = form["sch_s_service_id"]
            # ..
            sch_s_owner = request.user.user_id
            # ..
            number_on = datetime.strptime(str_date, settings.DATE)
            there_is = datetime.strptime(str_there_is, settings.DATE_T)
            # ...
            new = ScheduleService()
            new.name = name
            new.type_on = type_on
            new.number_on = number_on
            new.there_is = there_is
            new.title = title
            new.description = description
            new.sch_s_owner = sch_s_owner
            new.sch_s_service_id = int(sch_s_service_id)
            new.created_at = datetime.now()
            # ..
            session.add(new)
            session.refresh(new)
            await session.commit()
            # ..
            await send_mail(
                f"A new object has been created - {new}: {name}"
            )
            # ..
            response = RedirectResponse(
                f"/item/schedule-service/details/{ new.sch_s_service_id }/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def update_service(request):

    id = request.path_params["id"]
    template = "/schedule/update_service.html"

    async with async_session() as session:
        # ..
        detail = await in_schedule_service(request, session, id)
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
            str_date = form["dates"]
            str_there_is = form["there_is"]
            # ..
            name = form["name"]
            type_on = form["type_on"]
            title = form["title"]
            description = form["description"]
            # ..
            number_on = datetime.strptime(str_date, settings.DATE)
            there_is = datetime.strptime(str_there_is, settings.DATE_T)
            # ..
            query = (
                sqlalchemy_update(ScheduleService)
                .where(ScheduleService.id == id)
                .values(
                    name=name,
                    type_on=type_on,
                    number_on=number_on,
                    there_is=there_is,
                    title=title,
                    description=description,
                )
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            await send_mail(
                f"changes were made at the facility - {detail}: {detail.name}"
            )
            # ..
            response = RedirectResponse(
                f"/item/schedule-service/details/{detail.sch_s_service_id}/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def schedule_delete(request):

    id = request.path_params["id"]
    template = "/schedule/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            detail = await in_schedule_service(request, session, id)
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
            # ..
            query = (
                delete(ScheduleService)
                .where(ScheduleService.id == id)
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/schedule-service/list",
                status_code=302,
            )
            return response
    await engine.dispose()
