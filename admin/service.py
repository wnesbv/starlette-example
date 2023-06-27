
import json

from sqlalchemy import select, update as sqlalchemy_update, delete, func, and_

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from item.models import Service, ScheduleService
from make_an_appointment.models import ReserveServicerFor
from item.img import FileType
from .opt_slc import (
    in_admin,
    in_service,
    all_item,
    in_rent,
    all_schedule,
    all_service,
    all_count,
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
            # ..
            odj_count = await all_count(session)
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
            cmt_list = await service_comment(request, session)
            # ..
            detail = await in_service(request, session)
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
                    "id": to.id,
                    "date": to.date,
                    "name": to.name,
                    "type": to.type,
                    "there_is": to.there_is,
                    "description": to.description,
                }
                for to in obj_list
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
            # ..
            service_owner = request.user.user_id
            # ..
            file_obj = FileType.create_from(
                file=form["file"].file, original_filename=form["file"].filename
            )
            # ..
            new = Service(file=file_obj)
            new.title = title
            new.description = description
            new.file_obj = file_obj
            new.service_owner = service_owner
            # ..
            new.service_belongs = int(service_belongs)
            # ..
            session.add(new)
            session.refresh(new)
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
        detail = await in_service(request, session)
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
            detail.title = title
            detail.description = description
            # ...
            file_obj = FileType.create_from(
                file=form["file"].file, original_filename=form["file"].filename
            )
            # ..
            file_query = (
                sqlalchemy_update(Service)
                .where(Service.id == id)
                .values(file=file_obj, title=title, description=description)
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
            detail = await in_service(request, session)
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
