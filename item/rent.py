
import json
from datetime import datetime
from sqlalchemy import(
    update as sqlalchemy_update,
    delete
)
from sqlalchemy.future import select

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from mail.send import send_mail

from options_select.opt_slc import(
    user_tm,
    rent_comment,
    in_rent,
)
from .models import Rent, ScheduleRent
from .img import FileType


templates = Jinja2Templates(directory="templates")


async def rent_list(
    request
):
    template = "/item/rent/list.html"
    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(Rent).order_by(Rent.created_at.desc())
        )
        odj_list = stmt.scalars().all()
        #..
        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(
            template, context
        )
    await engine.dispose()


async def rent_details(
    request
):
    id = request.path_params["id"]
    template = "/item/rent/details.html"
    async with async_session() as session:
        #..
        cmt_list = await rent_comment(request, session)
        #..
        stmt = await session.execute(
            select(Rent)
            .where(Rent.id==id)
        )
        detail = stmt.scalars().first()
        #..
        stmt = await session.execute(
            select(ScheduleRent)
            .where(ScheduleRent.sch_r_rent_id==id)
            .order_by(ScheduleRent.id.desc())
        )
        obj_list = stmt.scalars().all()
        #..
        obj = [
            {
                "start": to.start,
                "end": to.end,
                "title": to.title,
            }
            for to in obj_list
        ]
        sch_json = json.dumps(obj, default=str)
        #..
        context = {
            "request": request,
            "detail": detail,
            "cmt_list": cmt_list,
            "obj_list": obj_list,
            "sch_json": sch_json,
        }
        return templates.TemplateResponse(
            template, context
        )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def rent_create(
    request
):
    template = "/item/rent/create.html"
    async with async_session() as session:
        if request.method == "GET":
            #..
            odj_item = await user_tm(request, session)
            #..
            return templates.TemplateResponse(
                template, {
                    "request": request,
                    "odj_item": odj_item,
                }
            )
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            title = form["title"]
            description = form["description"]
            rent_belongs = form["rent_belongs"]
            #..
            rent_owner = request.user.user_id
            #..
            file_obj = FileType.create_from(
                file=form["file"].file,
                original_filename=form["file"].filename
            )
            #..
            new = Rent(file=file_obj)
            new.title = title
            new.description = description
            new.file_obj = file_obj
            new.rent_owner = rent_owner
            #..
            new.rent_belongs = int(rent_belongs)
            #..
            new.created_at = datetime.now()
            
            session.add(new)
            session.refresh(new)
            await session.commit()
            #..
            await send_mail(
                f"A new object has been created - {new}: {title}"
            )
            #..
            response = RedirectResponse(
                f"/item/rent/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def rent_update(
    request
):
    id = request.path_params["id"]
    template = "/item/rent/update.html"
    async with async_session() as session:
        #..
        detail = await in_rent(request, session)
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
            title = form["title"]
            description = form["description"]
            #..
            file_obj = FileType.create_from(
                file=form["file"].file,
                original_filename=form["file"].filename
            )
            #..
            file_query = (
                sqlalchemy_update(Rent)
                .where(Rent.id == id)
                .values(
                    file=file_obj,
                    title=title,
                    description=description
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
                f"/item/rent/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def delete(
    request
):
    id = request.path_params["id"]
    template = "/item/rent/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            detail = await in_rent(request, session)
            #..
            if detail:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request
                    },
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            #..
            query = (
                delete(Rent).where(Rent.id == id)
            )
            #..
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/item/rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()
