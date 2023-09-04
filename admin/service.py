
from pathlib import Path
from datetime import datetime, date

import json

from sqlalchemy import select, update as sqlalchemy_update, delete, func, and_

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from account.models import User
from item.models import Service, ScheduleService

from make_an_appointment.models import ReserveServicerFor

from options_select.opt_slc import all_total, for_id

from .opt_slc import (
    in_admin,
    all_user,
    all_item,
    all_schedule,
    in_service,
    all_service,
    service_comment,
)
from . import img


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def i_list(request):
    # ..
    template = "/admin/service/list.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            stmt = await session.execute(select(Service).order_by(Service.id))
            obj_list = stmt.scalars().all()
            obj_count = await all_total(session, Service)
            # ..
            context = {
                "request": request,
                "obj_list": obj_list,
                "obj_count": obj_count,
            }
            return templates.TemplateResponse(template, context)
        return PlainTextResponse("You are banned - this is not your account..!")
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_details(request):
    # ..
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
            i = await in_service(session, id)
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
                "i": i,
                "cmt_list": cmt_list,
                "sch_json": sch_json,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


async def i_create(request):
    # ..
    basewidth = 800
    template = "/admin/service/create.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            owner_all = await all_user(session)
            obj_item = await all_item(session)
            # ..
            if admin:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "owner_all": owner_all,
                        "obj_item": obj_item,
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
            owner = form["owner"]
            service_belongs = form["service_belongs"]
            # ..
            if file.filename == "":
                new = Service()
                new.title = title
                new.description = description
                new.file = file
                new.owner = int(owner)
                new.service_belongs = int(service_belongs)
                # ..
                session.add(new)
                await session.commit()
                # ..
                return RedirectResponse(
                    f"/admin/service/details/{ new.id }",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, owner)
            new = Service()
            new.title = title
            new.description = description
            new.owner = int(owner)
            new.service_belongs = int(service_belongs)
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.flush()
            new.file = await img.service_img_creat(
                file, email.email, service_belongs, new.id, basewidth
            )
            session.add(new)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/admin/service/details/{ new.id }",
                status_code=302,
            )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_update(request):
    # ..
    basewidth = 800
    id = request.path_params["id"]
    template = "/admin/service/update.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        i = await in_service(session, id)
        # ..
        context = {
            "request": request,
            "i": i,
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
            del_obj = form.get("del_bool")
            # ..
            if file.filename == "":
                query = (
                    sqlalchemy_update(Service)
                    .where(Service.id == id)
                    .values(
                        title=title, description=description, file=i.file, modified_at=datetime.now(),
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
                    return RedirectResponse(
                        f"/admin/service/details/{id}",
                        status_code=302,
                    )
                return RedirectResponse(
                    f"/admin/service/details/{id}",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, i.owner)
            file_query = (
                sqlalchemy_update(Service)
                .where(Service.id == id)
                .values(
                    title=title,
                    description=description,
                    file=await img.service_img_creat(
                        file, email, i.service_belongs, i.id, basewidth
                    ),
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/service/details/{id}",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/service/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            i = await in_service(session, id)
            # ..
            if admin:
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
            i = await in_service(session, id)
            email = await for_id(session, User, i.owner)
            # ..
            await img.del_service(
                email.email, i.service_belongs, id
            )
            # ..
            await session.delete(i)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/admin/service/list",
                status_code=302,
            )
            return response
    await engine.dispose()
