
from pathlib import Path
from datetime import datetime
from sqlalchemy import update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from mail.send import send_mail

from options_select import file_img
from options_select.opt_slc import item_comment, in_item_user

from .models import Item, Service, Rent


templates = Jinja2Templates(directory="templates")


async def item_create(request):

    template = "/item/create.html"
    mdl = "item"
    basewidth = 800

    async with async_session() as session:
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
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            item_owner = request.user.user_id
            # ..
            if file.filename == "":
                new = Item()
                new.title = title
                new.item_owner = item_owner
                new.description = description
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

            new = Item()
            new.title = title
            new.file = await file_img.img_creat(request, file, mdl, basewidth)
            new.item_owner = item_owner
            new.description = description
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

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_update(request):
    
    id = request.path_params["id"]
    template = "/item/update.html"
    mdl = "item"
    basewidth = 800

    async with async_session() as session:
        # ..
        i = await in_item_user(request, session, id)
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
                        title=title, description=description, file=i.file
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

            file_query = (
                sqlalchemy_update(Item)
                .where(Item.id == id)
                .values(
                    title=title,
                    description=description,
                    file=await file_img.img_creat(request, file, mdl, basewidth),
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


@requires("authenticated", redirect="user_login")
# ...
async def item_delete(request):

    id = request.path_params["id"]
    template = "/item/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await in_item_user(request, session, id)
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
            query = delete(Item).where(Item.id == id)
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()


async def item_list(request):

    template = "/item/list.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(select(Item).order_by(Item.created_at.desc()))
        odj_list = stmt.scalars().all()
        # ..
        context = {
            "request": request,
            "odj_list": odj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def item_details(request):

    id = request.path_params["id"]
    template = "/item/details.html"

    async with async_session() as session:
        # ..
        cmt_list = await item_comment(session, id)
        # ...
        stmt = await session.execute(select(Item).where(Item.id == id))
        i = stmt.scalars().first()
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
