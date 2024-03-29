
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

from account.models import User
from item.models import Rent, Service, ScheduleService, MyEnum

from options_select.opt_slc import for_id, for_in

from .opt_slc import (
    admin,
    get_admin_user,
    details_schedule_service,
)


templates = Jinja2Templates(directory="templates")


@admin()
# ...
async def sch_list(request):
    # ..
    template = "/admin/schedule_service/list.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            # ..
            obj_list = await for_in(session, ScheduleService)
            context = {
                "request": request,
                "obj_list": obj_list,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@admin()
# ...
async def user_list(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/schedule_service/user_list.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            # ..
            stmt = await session.execute(
                select(ScheduleService).where(ScheduleService.owner == id)
            )
            obj_list = stmt.scalars().all()
            # ..
            context = {
                "request": request,
                "obj_list": obj_list,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@admin()
# ...
async def srv_list(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/schedule_service/srv_list.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            # ..
            stmt = await session.execute(
                select(ScheduleService)
                .where(ScheduleService.sch_s_service_id == id)
            )
            obj_list = stmt.scalars().all()
            # ..
            context = {
                "request": request,
                "obj_list": obj_list,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@admin()
# ...
async def all_user_sch_list(request):
    # ..
    template = "/admin/schedule_service/all_user_sch_list.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            # ..
            stmt = await session.execute(
                select(ScheduleService.id).join(ScheduleService.sch_s_service)
            )
            result = stmt.scalars().all()
            i = await session.execute(select(Service).where(Service.id.not_in(result)))
            not_service_list = i.scalars().all()
            # ..
            stmt = await session.execute(
                select(ScheduleService.id).join(ScheduleService.sch_s_user)
            )
            result = stmt.scalars().all()
            i = await session.execute(select(User).where(User.id.not_in(result)))
            not_sch_user_list = i.scalars().all()
            # ..
            # ..
            stmt = await session.execute(
                select(ScheduleService.id).join(ScheduleService.sch_s_service)
            )
            result = stmt.scalars().all()
            i = await session.execute(select(Service).where(Service.id.in_(result)))
            service_list = i.scalars().all()
            # ..
            stmt = await session.execute(
                select(ScheduleService.id).join(ScheduleService.sch_s_user)
            )
            result = stmt.scalars().all()
            i = await session.execute(select(User).where(User.id.in_(result)))
            sch_user_list = i.scalars().all()
            # ..
            context = {
                "request": request,
                "service_list": service_list,
                "sch_user_list": sch_user_list,
                "not_service_list": not_service_list,
                "not_sch_user_list": not_sch_user_list,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@admin()
# ...
async def srv_id_sch_id(request):
    # ..
    id = request.path_params["id"]
    service = request.path_params["service"]
    template = "/admin/schedule_service/srv_id_sch_id.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            # ..
            if obj:
                # ..
                obj_list = await details_schedule_service(session, service)
                # ..
                obj = [
                    {
                        "id": i.id,
                        "owner": i.owner,
                        "name": i.name,
                        "title": i.title,
                        "description": i.description,
                        "type_on": i.type_on.name,
                        "number_on": i.number_on,
                        "there_is": i.there_is,
                        "sch_s_service_id": i.sch_s_service_id,
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
                i = await for_id(session, ScheduleService, id)
                context = {
                    "request": request,
                    "sch_json": sch_json,
                    "i": i,
                }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@admin()
# ...
async def details(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/schedule_service/details.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            # ..
            if obj:
                # ..
                i = await for_id(session, ScheduleService, id)
                context = {
                    "request": request,
                    "i": i,
                }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@admin()
# ...
async def sch_create(request):
    # ..
    template = "/admin/schedule_service/create.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            obj_service = await for_in(session, Service)
            obj_rent = await for_in(session, Rent)
            objects = list(MyEnum)
            # ..
            if obj:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "obj_rent": obj_rent,
                        "obj_service": obj_service,
                        "objects": objects,
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
            title = form["title"]
            description = form["description"]
            type_on = form["type_on"]
            sch_s_service_id = form["sch_s_service_id"]
            # ..
            owner = request.user.user_id
            # ..
            number_on = datetime.strptime(str_date, settings.DATE)
            there_is = datetime.strptime(str_there_is, settings.DATE_T)
            # ...
            new = ScheduleService()
            new.name = name
            new.title = title
            new.description = description
            new.type_on = type_on
            new.number_on = number_on
            new.there_is = there_is
            new.owner = owner
            new.sch_s_service_id = int(sch_s_service_id)
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/scheduleservice/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@admin()
# ...
async def sch_update(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/schedule_service/update.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        i = await for_id(session, ScheduleService, id)
        # ..
        objects = list(MyEnum)
        context = {
            "request": request,
            "i": i,
            "objects": objects,
        }
        # ...
        if request.method == "GET":
            if obj:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            str_date = form["number_on"]
            str_there_is = form["there_is"]
            # ..
            name = form["name"]
            title = form["title"]
            description = form["description"]
            type_on = form["type_on"]
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
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/scheduleservice/details/{ i.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@admin()
# ...
async def sch_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/schedule_service/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            i = await for_id(session, ScheduleService, id)
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
            query = delete(ScheduleService).where(ScheduleService.id == id)
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
async def delete_service_csv(request):
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
                    "/admin/scheduleservice/list",
                    status_code=302,
                )
                return response
    await engine.dispose()
