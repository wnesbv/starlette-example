
from pathlib import Path
from datetime import datetime
import json

from sqlalchemy import update as sqlalchemy_update, delete, and_
from sqlalchemy.future import select
from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from mail.send import send_mail

from options_select.opt_slc import (
    user_tm,
    service_comment,
    in_service,
)
from make_an_appointment.models import ReserveServicerFor

from .models import Service, ScheduleService
from .img import FileType, BASE_DIR


templates = Jinja2Templates(directory="templates")


async def service_list(request):
    template = "/item/service/list.html"

    async with async_session() as session:
        # ..
        result = await session.execute(
            select(Service)
            .order_by(Service.id)
        )
        odj_list = result.scalars().all()
        # ..
        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def service_details(request):
    id = request.path_params["id"]
    template = "/item/service/details.html"

    async with async_session() as session:
        # ..
        cmt_list = await service_comment(request, session)
        # ..
        stmt = await session.execute(
            select(Service)
            .where(Service.id == id)
        )
        detail = stmt.scalars().first()
        #..
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
                "date": i.date,
                "name": i.name,
                "type": i.type,
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


@requires("authenticated", redirect="user_login")
# ...
async def service_create(request):

    template = "/item/service/create.html"

    async with async_session() as session:
        # ...
        if request.method == "GET":
            # ..
            odj_item = await user_tm(request, session)
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
            service_owner = request.user.user_id
            # ..
            file_obj = FileType.create_from(
                file=form["file"].file,
                original_filename=form["file"].filename
            )
            # ..
            new = Service(file=file_obj)
            new.title = title
            new.description = description
            new.file_obj = file_obj
            new.service_owner = service_owner
            new.service_belongs = int(service_belongs)
            new.created_at = datetime.now()
            # ..
            session.add(new)
            session.refresh(new)
            await session.commit()
            # ..
            await send_mail(f"A new object has been created - {new}: {title}")
            # ..
            response = RedirectResponse(
                f"/item/service/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def service_update(request):

    id = request.path_params["id"]
    template = "/item/service/update.html"

    async with async_session() as session:
        # ..
        detail = await in_service(request, session)
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
            title = form["title"]
            description = form["description"]
            # ..
            query = (
                sqlalchemy_update(Service)
                .where(Service.id == id)
                .values(
                    title=title,
                    description=description
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            # ..
            await send_mail(
                f"changes were made at the facility - {detail}: {detail.title}"
            )
            # ..
            response = RedirectResponse(
                f"/item/service/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def file_update(
    request
):
    id = request.path_params["id"]
    template = "/item/service/update_file.html"

    async with async_session() as session:
        #..
        detail = await in_service(request, session)
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
            #..
            form = await request.form()
            #..
            file_obj = FileType.create_from(
                file=form["file"].file,
                original_filename=form["file"].filename
            )
            #..
            file_query = (
                sqlalchemy_update(Service)
                .where(Service.id == id)
                .values(
                    file=file_obj,
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()
            #..
            await send_mail(
                f"changes were made at the facility - {detail}: {detail.title}"
            )
            #..
            response = RedirectResponse(
                f"/item/service/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def delete(request):

    id = request.path_params["id"]
    template = "/item/service/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            detail = await in_service(request, session)
            if detail:
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
                "/item/service/list",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def file_delete(
    request
):

    id = request.path_params["id"]

    async with async_session() as session:

        if request.method == "GET":
            # ..
            detail = await in_service(request, session)
            if detail:
                # ..
                root_directory = (
                    BASE_DIR
                    / f"static/upload/img/{detail.file.saved_filename}"
                )
                Path(root_directory).unlink()
                # ..
                file_query = (
                    sqlalchemy_update(Service)
                    .where(Service.id == id)
                    .values(
                        file=None,
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(file_query)
                await session.commit()
                # ..
                return RedirectResponse(
                    f"/item/details/{detail.id}",
                    status_code=302,
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
    await engine.dispose()
