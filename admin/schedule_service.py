
from pathlib import Path

import json

from sqlalchemy import update as sqlalchemy_update, delete

from sqlalchemy.future import select

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from json2html import json2html

from db_config.storage_config import engine, async_session

from account.models import User
from item.models import Service, ScheduleService

from options_select.opt_slc import (
    details_schedule_service,
)

from .opt_slc import(
    in_admin,
    in_schedule_sv,
    all_service,
    all_rent,
)


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
root_directory = BASE_DIR / "static/upload"


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def user_list(
    request
):

    template = "/admin/schedule_service/user_list.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            stmt = await session.execute(
                select(User.id)
                .join(Service.service_sch_s)
            )
            result = stmt.scalars().all()
            sv = await session.execute(
                select(User)
                .where(User.id.in_(result))
            )
            odj_list = sv.scalars().all()
            # ..
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
async def item_list(
    request
):

    user = request.path_params["user"]
    template = "/admin/schedule_service/list.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            stmt = await session.execute(
                select(Service)
                .where(Service.service_owner == user)
            )
            odj_list = stmt.scalars().all()
            # ..
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
async def item_details(
    request
):

    service = request.path_params["service"]
    template = "/admin/schedule_service/details.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            # ..
            if admin:
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
                # ..
                table_attributes = "style='width:100%', class='table table-bordered'"
                sch_json = json2html.convert(
                    json = sch_json,
                    table_attributes=table_attributes
                )
                # ..
                context = {
                    "request": request,
                    "sch_json": sch_json,
                }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_create(
    request
):

    template = "/admin/schedule_service/create.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            odj_service = await all_service(session)
            odj_rent = await all_rent(session)
            # ..
            if admin:
                return templates.TemplateResponse(
                    template, {
                        "request": request,
                        "odj_rent": odj_rent,
                        "odj_service": odj_service,
                    }
                )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ...
            title = form["title"]
            description = form["description"]
            # ...
            by_points = form["by_points"]
            by_choose = form["by_choose"]
            # ...
            sch_s_service_id = form["sch_s_service_id"]
            sch_r_rent_id = form["sch_r_rent_id"]
            # ..
            sch_owner = request.user.user_id
            # ..
            new = ScheduleService()
            new.title = title
            new.description = description
            new.by_choose = by_choose
            new.by_points = by_points
            new.sch_owner = sch_owner
            # ..
            new.sch_s_service_id = sch_s_service_id
            new.sch_r_rent_id = sch_r_rent_id
            # ..
            session.add(new)
            session.refresh(new)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/schedule-service/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_update(
    request
):

    id = request.path_params["id"]
    template = "/admin/schedule_service/update.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        detail = await in_schedule_sv(session, id)
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if admin:
                return templates.TemplateResponse(
                    template, context
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            detail.title = form["title"]
            detail.description = form["description"]
            detail.by_points = form["by_points"]
            # ..
            query = (
                sqlalchemy_update(ScheduleService)
                .where(ScheduleService.id == id)
                .values(form)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/schedule_service/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_delete(
    request
):

    id = request.path_params["id"]
    template = "/admin/schedule_service/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            detail = await in_schedule_sv(session, id)
            # ..
            if admin:
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
                "/admin/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def delete_service_csv(request):

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            # ..
            if admin:
                directory = (
                    BASE_DIR
                    / "static/service/"
                )
                response = [f.unlink() for f in Path(directory).glob("*") if f.is_file()]
                response = RedirectResponse(
                    "/item/schedule-service/list_service",
                    status_code=302,
                )
                return response
    await engine.dispose()
