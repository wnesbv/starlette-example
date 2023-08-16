
from pathlib import Path
import json
from datetime import datetime
from sqlalchemy import update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from mail.send import send_mail

from options_select import file_img
from options_select.opt_slc import (
    user_tm,
    rent_comment,
    in_rent_user,
)
from .models import Rent, ScheduleRent


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def rent_create(request):

    template = "/rent/create.html"
    mdl = "rent"
    basewidth = 800

    async with async_session() as session:
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
            rent_belongs = form["rent_belongs"]
            # ..
            if file.filename == "":

                new = Rent()
                new.title = title
                new.description = description
                new.rent_owner = request.user.user_id
                # ..
                new.rent_belongs = int(rent_belongs)
                # ..
                new.created_at = datetime.now()

                session.add(new)
                await session.commit()
                # ..
                await send_mail(f"A new object has been created - {new}: {title}")
                # ..
                return RedirectResponse(
                    f"/item/rent/details/{ new.id }",
                    status_code=302,
                )

            new = Rent()
            new.title = title
            new.description = description
            new.file = await file_img.img_creat(request, file, mdl, basewidth)
            new.rent_owner = request.user.user_id
            # ..
            new.rent_belongs = int(rent_belongs)
            # ..
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            await send_mail(f"A new object has been created - {new}: {title}")
            # ..
            return RedirectResponse(
                f"/item/rent/details/{ new.id }",
                status_code=302,
            )

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def rent_update(request):

    id = request.path_params["id"]
    template = "/rent/update.html"
    mdl = "rent"
    basewidth = 800

    async with async_session() as session:
        # ..
        i = await in_rent_user(request, session, id)
        # ..
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
            description = form["description"]
            file = form["file"]
            del_obj = form.get("del_bool")
            # ..

            if file.filename == "":
                query = (
                    sqlalchemy_update(Rent)
                    .where(Rent.id == id)
                    .values(title=title, description=description, file=i.file)
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(query)
                await session.commit()

                if del_obj:
                    if Path(f".{i.file}").exists():
                        Path.unlink(f".{i.file}")

                    fle_not = (
                        sqlalchemy_update(Rent)
                        .where(Rent.id == id)
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
                        f"/item/rent/details/{id}",
                        status_code=302,
                    )
                return RedirectResponse(
                    f"/item/rent/details/{id}",
                    status_code=302,
                )

            file_query = (
                sqlalchemy_update(Rent)
                .where(Rent.id == id)
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
                f"/item/rent/details/{id}",
                status_code=302,
            )

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def rent_delete(request):

    id = request.path_params["id"]
    template = "/rent/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await in_rent_user(request, session, id)
            # ..
            if i:
                return templates.TemplateResponse(
                    template,
                    {"request": request},
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            query = delete(Rent).where(Rent.id == id)
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()


async def rent_list(request):

    template = "/rent/list.html"
    
    async with async_session() as session:
        # ..
        stmt = await session.execute(select(Rent).order_by(Rent.created_at.desc()))
        odj_list = stmt.scalars().all()
        # ..
        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def rent_details(request):

    id = request.path_params["id"]
    template = "/rent/details.html"

    async with async_session() as session:
        # ..
        cmt_list = await rent_comment(session, id)
        # ..
        stmt = await session.execute(select(Rent).where(Rent.id == id))
        i = stmt.scalars().first()
        # ..
        stmt = await session.execute(
            select(ScheduleRent)
            .where(ScheduleRent.sch_r_rent_id == id)
            .order_by(ScheduleRent.id.desc())
        )
        obj_list = stmt.scalars().all()
        # ..
        obj = [
            {
                "start": to.start,
                "end": to.end,
                "title": to.title,
            }
            for to in obj_list
        ]
        sch_json = json.dumps(obj, default=str)
        # ..
        context = {
            "request": request,
            "i": i,
            "cmt_list": cmt_list,
            "obj_list": obj_list,
            "sch_json": sch_json,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()
