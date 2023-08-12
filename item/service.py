
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

from make_an_appointment.models import ReserveServicerFor

from .models import Service, ScheduleService

from options_select import file_img
from options_select.opt_slc import (
    user_tm,
    service_comment,
    in_service_user,
)


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def service_create(request):

    template = "/item/service/create.html"
    mdl = "service"
    basewidth = 800

    async with async_session() as session:
        # ...
        if request.method == "GET":
            # ..
            odj_item = await user_tm(request, session)
            # ..
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
            file = form["file"]
            service_belongs = form["service_belongs"]
            # ..
            if file.filename == "":

                new = Service()
                new.title = title
                new.description = description
                new.service_owner = request.user.user_id
                # ..
                new.service_belongs = int(service_belongs)
                # ..
                new.created_at = datetime.now()
                # ..
                session.add(new)
                session.refresh(new)
                await session.commit()
                # ..
                await send_mail(f"A new object has been created - {new}: {title}")
                # ..
                return RedirectResponse(
                    f"/item/service/details/{ new.id }",
                    status_code=302,
                )

            new = Service()
            new.title = title
            new.description = description
            new.file = await file_img.img_creat(request, file, mdl, basewidth)
            new.service_owner = request.user.user_id
            # ..
            new.service_belongs = int(service_belongs)
            # ..
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            await send_mail(f"A new object has been created - {new}: {title}")
            # ..
            return RedirectResponse(
                f"/item/service/details/{ new.id }",
                status_code=302,
            )

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def service_update(request):

    id = request.path_params["id"]
    template = "/item/service/update.html"

    async with async_session() as session:
        # ..
        i = await in_service_user(request, session, id)
        context = {
            "request": request,
            "i": i,
        }
        # ...
        if request.method == "GET":
            if i:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            file = form["file"]
            description = form["description"]
            # ..

            if file.filename == "":

                query = (
                    sqlalchemy_update(Service)
                    .where(Service.id == id)
                    .values(
                        title=title,
                        description=description,
                        file=i.file,
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(query)
                await session.commit()

                if del_obj:
                    if Path(f".{i.file}").exists():
                        Path.unlink(f".{i.file}")

                    fle_not = (
                        sqlalchemy_update(Service)
                        .where(Service.id == id)
                        .values(file=None, modified_at=datetime.now())
                        .execution_options(synchronize_session="fetch")
                    )
                    await session.execute(fle_not)
                    await session.commit()
                    # ..
                    await send_mail(
                        f"changes were made at the facility - {i}: {i.title}"
                    )
                    # ..
                    return RedirectResponse(
                        f"/item/service/details/{id}",
                        status_code=302,
                    )
                return RedirectResponse(
                    f"/item/service/details/{id}",
                    status_code=302,
                )


            file_query = (
                sqlalchemy_update(Service)
                .where(Service.id == id)
                .values(
                    title=title,
                    description=description,
                    file=await file_img.img_creat(request, file, mdl, basewidth),
                )
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(file_query)
            await session.commit()
            # ..
            await send_mail(
                f"changes were made at the facility - {i}: {i.title}"
            )
            # ..
            return RedirectResponse(
                f"/item/service/details/{id}",
                status_code=302,
            )

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def delete(request):

    id = request.path_params["id"]
    template = "/item/service/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            i = await in_service_user(request, session, id)
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
        cmt_list = await service_comment(session, id)
        # ..
        stmt = await session.execute(
            select(Service)
            .where(Service.id == id)
        )
        i = stmt.scalars().first()
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
            "i": i,
            "cmt_list": cmt_list,
            "sch_json": sch_json,
        }

        return templates.TemplateResponse(template, context)
    await engine.dispose()