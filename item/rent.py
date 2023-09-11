from pathlib import Path
from datetime import datetime

import json

from sqlalchemy import update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from admin import img
from mail.send import send_mail
from account.models import User

from options_select.opt_slc import (
    owner_prv,
    for_id,
    rent_comment,
    and_owner_request,
    id_fle_delete,
)
from auth_privileged.views import get_privileged_user
from .models import Item, Rent, ScheduleRent


templates = Jinja2Templates(directory="templates")


# ...
async def rent_create(request):
    # ..
    basewidth = 800
    template = "/rent/create.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if request.method == "GET":
            # ..
            obj_item = await owner_prv(session, Item, prv)
            # ..
            if obj_item:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "obj_item": obj_item,
                    },
                )
            return RedirectResponse("/item/create")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            rent_belongs = form["rent_belongs"]
            owner = prv.id
            # ..
            if file.filename == "":
                # ..
                new = Rent()
                new.title = title
                new.description = description
                new.owner = request.user.user_id
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
            # ..
            email = await for_id(session, User, owner)
            # ..
            new = Rent()
            new.title = title
            new.description = description
            new.owner = owner
            new.rent_belongs = int(rent_belongs)
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.flush()
            new.file = await img.rent_img_creat(
                file, email.email, rent_belongs, new.id, basewidth
            )
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


# ...
async def rent_update(request):
    # ..
    basewidth = 800
    id = request.path_params["id"]
    template = "/rent/update.html"

    async with async_session() as session:
        # ..
        i = await and_owner_request(request, session, Rent, id)
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
                    .values(
                        title=title,
                        description=description,
                        file=i.file,
                        modified_at=datetime.now(),
                    )
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
            # ..
            email = await for_id(session, User, i.owner)
            file_query = (
                sqlalchemy_update(Rent)
                .where(Rent.id == id)
                .values(
                    title=title,
                    description=description,
                    file=await img.rent_img_creat(
                        file, email.email, i.rent_belongs, i.id, basewidth
                    ),
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(file_query)
            await session.commit()
            # ..
            await send_mail(f"changes were made at the facility - {i}: {i.title}")
            # ..
            return RedirectResponse(
                f"/item/rent/details/{id}",
                status_code=302,
            )

    await engine.dispose()


# ...
async def rent_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/rent/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await and_owner_request(request, session, Rent, id)
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
            i = await and_owner_request(request, session, Rent, id)
            email = await for_id(session, User, i.owner)
            # ..
            await img.del_rent(email.email, i.rent_belongs, id)
            # ..
            await session.delete(i)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()


async def rent_list(request):
    # ..
    template = "/rent/list.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(select(Rent).order_by(Rent.created_at.desc()))
        obj_list = stmt.scalars().all()
        # ..
        context = {
            "request": request,
            "obj_list": obj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def rent_details(request):
    # ..
    id = request.path_params["id"]
    template = "/rent/details.html"

    async with async_session() as session:
        # ..
        cmt_list = await rent_comment(session, id)
        # ..
        i = await for_id(session, Rent, id)
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
