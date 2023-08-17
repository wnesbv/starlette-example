
import json

from sqlalchemy import select, update as sqlalchemy_update, delete, func, and_

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from item.models import Service, ScheduleService
from make_an_appointment.models import ReserveServicerFor
from options_select.opt_slc import all_total

from .opt_slc import (
    in_admin,
    in_service,
    all_item,
    all_schedule,
    all_service,
    service_comment,
)


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def item_list(request):

    template = "/admin/service/list.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            stmt = await session.execute(select(Service).order_by(Service.id))
            odj_list = stmt.scalars().all()
            odj_count = await all_total(session, Service)
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
    template = "/admin/service/details.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            cmt_list = await service_comment(session, id)
            # ..
            detail = await in_service(session, id)
            # ..
            rsv = await session.execute(
                select(ScheduleService.id)
                .join(ReserveServicerFor.rsf_sch_s)
                .where(
                    ScheduleService.sch_s_service_id == id,
                )
            )
            rsv_list = rsv.scalars().all()
            #..
            stmt = await session.execute(
                select(ScheduleService)
                .where(
                    and_(
                        ScheduleService.id.not_in(rsv_list),
                        ScheduleService.sch_s_service_id == id,
                    )
                )
            )
            obj_list = stmt.scalars().all()
            # ..
            obj = [
                {
                    "id": i.id,
                    "name": i.name,
                    "type_on": i.type_on,
                    "number_on": i.number_on,
                    "there_is": i.there_is,
                    "description": i.description,
                }
                for i in obj_list
            ]
            sch_json = json.dumps(obj, default=str)
            # ..
            context = {
                "request": request,
                "detail": detail,
                "cmt_list": cmt_list,
                "sch_json": sch_json,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


async def item_create(request):

    template = "/admin/service/create.html"

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
            service_belongs = form["service_belongs"]
            file = form["file"]
            # ..
            service_owner = request.user.user_id
            # ..
            new = Service()
            new.title = title
            new.description = description
            new.file = file
            new.service_owner = service_owner
            # ..
            new.service_belongs = int(service_belongs)
            # ..
            session.add(new)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/service/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_update(request):

    id = request.path_params["id"]
    template = "/admin/service/update.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        detail = await in_service(session, id)
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
            detail.title = title
            detail.description = description
            # ..
            file_query = (
                sqlalchemy_update(Service)
                .where(Service.id == id)
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
                f"/admin/service/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_delete(request):

    id = request.path_params["id"]
    template = "/admin/service/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            detail = await in_service(session, id)
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
            query = delete(Service).where(Service.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/admin/service/list",
                status_code=302,
            )
            return response
    await engine.dispose()
