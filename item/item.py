
from pathlib import Path
from datetime import datetime

from sqlalchemy import update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from admin import img
from mail.send import send_mail
from account.models import User

from options_select.opt_slc import for_id, item_comment, and_owner_request, owner_request

from options_select.csv_import import import_csv
from options_select.csv_export import export_csv

from auth_privileged.views import get_privileged_user, privileged

from .models import Item, Service, Rent
from config.settings import BASE_DIR


templates = Jinja2Templates(directory="templates")


@privileged()
# ...
async def export_item_csv(request):
    async with async_session() as session:
        # ..
        if request.method == "GET":
            # ..
            result = await owner_request(request, session, Item)
            # ..
            await export_csv(request, result)
            # ..
            user = request.user.email
            directory = BASE_DIR / f"static/csv/{user}/export_csv.csv"
            if Path(directory).exists():
                return RedirectResponse(f"/static/csv/{user}/export_csv.csv")
            # ..
    await engine.dispose()


@privileged()
# ...
async def import_item_csv(request):
    # ..
    template = "/item/item_import_csv.html"

    async with async_session() as session:
        # ..
        if request.method == "GET":
            response = templates.TemplateResponse(
                template,
                {
                    "request": request,
                },
            )
            if not request.user.is_authenticated:
                response = RedirectResponse(
                    "/account/login",
                    status_code=302,
                )
            return response
        # ...
        if request.method == "POST":
            # ..
            await import_csv(request, Item, session)
            await session.commit()
            # ..
            return RedirectResponse(
                "/item/list",
                status_code=302,
            )

    await engine.dispose()


@privileged()
# ...
async def item_create(request):
    # ..
    basewidth = 800
    template = "/item/create.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if request.method == "GET":
            response = templates.TemplateResponse(
                template,
                {
                    "request": request,
                },
            )
            if request.auth is False:
                response = RedirectResponse(
                    "/privileged/login",
                    status_code=302,
                )
            return response
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            owner = prv.id
            # ..
            if file.filename == "":
                new = Item()
                new.title = title
                new.description = description
                new.owner = owner
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
                # ..
                await send_mail(f"A new object has been created - {new}: {title}")
                # ..
                return RedirectResponse(
                    f"/item/details/{ new.id }",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, owner)
            new = Item()
            new.title = title
            new.description = description
            new.owner = owner
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.flush()
            # ..
            new.file = await img.item_img_creat(file, email.email, new.id, basewidth)
            session.add(new)
            await session.commit()
            # ..
            await send_mail(f"A new object has been created - {new}: {title}")
            # ..
            return RedirectResponse(
                f"/item/details/{ new.id }",
                status_code=302,
            )

    await engine.dispose()


@privileged()
# ...
async def item_update(request):
    # ..
    basewidth = 800
    id = request.path_params["id"]
    template = "/item/update.html"

    async with async_session() as session:
        # ..
        i = await and_owner_request(request, session, Item, id)
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
                    sqlalchemy_update(Item)
                    .where(Item.id == id)
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
                        sqlalchemy_update(Item)
                        .where(Item.id == id)
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
                        f"/item/details/{id}",
                        status_code=302,
                    )
                return RedirectResponse(
                    f"/item/details/{id}",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, i.owner)
            file_query = (
                sqlalchemy_update(Item)
                .where(Item.id == id)
                .values(
                    title=title,
                    description=description,
                    file=await img.item_img_creat(file, email.email, id, basewidth),
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
                f"/item/details/{id}",
                status_code=302,
            )
    await engine.dispose()


@privileged()
# ...
async def item_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/item/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await and_owner_request(request, session, Item, id)
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
            i = await and_owner_request(request, session, Item, id)
            email = await for_id(session, User, i.owner)
            # ..
            await img.del_tm(email.email, i.id)
            # ..
            await session.delete(i)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()


async def item_list(request):
    # ..
    template = "/item/list.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(select(Item).order_by(Item.created_at.desc()))
        obj_list = stmt.scalars().all()
        # ..
        context = {
            "request": request,
            "obj_list": obj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def item_details(request):
    # ..
    id = request.path_params["id"]
    template = "/item/details.html"

    async with async_session() as session:
        # ..
        cmt_list = await item_comment(session, id)
        # ...
        i = await for_id(session, Item, id)
        # ..
        if i:
            stmt = await session.execute(select(Rent).where(Rent.rent_belongs == id))
            all_rent = stmt.scalars().all()
            # ..
            stmt = await session.execute(
                select(Service).where(Service.service_belongs == id)
            )
            all_service = stmt.scalars().all()
            # ..
            context = {
                "request": request,
                "i": i,
                "cmt_list": cmt_list,
                "all_rent": all_rent,
                "all_service": all_service,
            }
            # ..
            return templates.TemplateResponse(template, context)
        return RedirectResponse("/item/list", status_code=302)
    await engine.dispose()


async def search(request):
    # ..
    query = request.query_params.get("query")
    template = "/item/search.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            stmt = await session.execute(
                select(Item).where(Item.title.like("%" + query + "%"))
            )
            search_title = stmt.scalars().all()
            # ...
            context = {
                "request": request,
                "search_title": search_title,
            }
            # ..
            return templates.TemplateResponse(template, context)
    await engine.dispose()
