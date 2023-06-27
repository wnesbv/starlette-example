
from pathlib import Path
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

from options_select.opt_slc import item_comment, in_item

from .models import Item, Service, Rent
from .img import FileType, BASE_DIR


templates = Jinja2Templates(directory="templates")


async def item_list(
    request
):
    template = "/item/list.html"

    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(Item)
            .order_by(Item.created_at.desc())
        )
        odj_list = stmt.scalars().all()
        #..
        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def item_details(
    request
):
    id = request.path_params["id"]
    template = "/item/details.html"

    async with async_session() as session:
        #..
        cmt_list = await item_comment(request, session)
        #...
        stmt = await session.execute(
            select(Item)
            .where(Item.id==id)
        )
        detail = stmt.scalars().first()
        #..
        if detail:
            stmt = await session.execute(
                select(Rent)
                .where(Rent.rent_belongs==id)
            )
            all_rent = stmt.scalars().all()
            #..
            stmt = await session.execute(
                select(Service)
                .where(Service.service_belongs==id)
            )
            all_service = stmt.scalars().all()
            #..
            context = {
                "request": request,
                "detail": detail,
                "cmt_list": cmt_list,
                "all_rent": all_rent,
                "all_service": all_service,
            }
            #..
            return templates.TemplateResponse(
                template, context
            )
        return RedirectResponse("/item/list", status_code=302)
    await engine.dispose()


async def item_create(
    request
):
    template = "/item/create.html"
    async with async_session() as session:

        if request.method == "GET":
            response = templates.TemplateResponse(
                template, {"request": request,}
            )
            if not request.user.is_authenticated:
                response = RedirectResponse(
                    "/account/login",
                    status_code=302,
                )
            return response
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            title = form["title"]
            description = form["description"]
            item_owner = request.user.user_id
            #..
            file_obj = FileType.create_from(
                file=form["file"].file,
                original_filename=form["file"].filename
            )
            #..
            new = Item(file=file_obj)
            new.title = title
            new.file_obj = file_obj
            new.item_owner = item_owner
            new.description = description
            new.created_at = datetime.now()
            #..
            session.add(new)
            session.refresh(new)
            await session.commit()
            #..
            await send_mail(
                f"A new object has been created - {new}: {title}"
            )
            #..
            response = RedirectResponse(
                f"/item/details/{ new.id }",
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
    template = "/item/update.html"

    async with async_session() as session:
        #..
        detail = await in_item(request, session)
        #..
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail and request.user.user_id == detail.item_owner:
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
            query = (
                sqlalchemy_update(Item)
                .where(Item.id == id)
                .values(
                    title=title,
                    description=description
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            #..
            await send_mail(
                f"changes were made at the facility - {detail}: {detail.title}"
            )
            #..
            response = RedirectResponse(
                f"/item/details/{detail.id}",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_file_update(
    request
):
    id = request.path_params["id"]
    template = "/item/update_file.html"

    async with async_session() as session:
        #..
        detail = await in_item(request, session)
        #..
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail and request.user.user_id == detail.item_owner:
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
                sqlalchemy_update(Item)
                .where(Item.id == id)
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
                f"/item/details/{detail.id}",
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
    template = "/item/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            detail = await in_item(request, session)
            if detail:
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
            #..
            query = (
                delete(Item)
                .where(Item.id == id)
            )
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/item/list",
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
        # ...
        if request.method == "GET":
            # ..
            detail = await in_item(request, session)
            if detail:
                # ..
                root_directory = (
                    BASE_DIR
                    / f"static/upload/img/{detail.file.saved_filename}"
                )
                Path(root_directory).unlink()
                # ..
                file_query = (
                    sqlalchemy_update(Item)
                    .where(Item.id == id)
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


async def search(
    request
):

    query = request.query_params.get("query")
    template = "/item/search.html"
    async with async_session() as session:

        if request.method == "GET":
            #..
            stmt = await session.execute(
                select(Item)
                .where(Item.title.like("%"+query+"%"))
            )
            search_title = stmt.scalars().all()
            #...
            context = {
                "request": request,
                "search_title": search_title,
            }
            #..
            return templates.TemplateResponse(
                template, context
            )
    await engine.dispose()
