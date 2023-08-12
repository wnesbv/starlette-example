
from sqlalchemy import select, update as sqlalchemy_update, delete, func

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from item.models import Item, Service, Rent
from .opt_slc import in_admin, all_user, item_comment, in_item


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def all_list(
    request
):
    template = "/admin/index.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            return templates.TemplateResponse(
                template, {"request": request,}
            )
        return PlainTextResponse(
            "You are banned - this is not your account..!"
        )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_list(
    request
):
    template = "/admin/list.html"
    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            stmt = await session.execute(
                select(Item)
                .order_by(Item.created_at)
            )
            odj_list = stmt.scalars().all()
            # ..
            stmt = await session.execute(
                select(func.count(Item.id))
            )
            odj_count = stmt.scalars().all()
            # ..
            context = {
                "request": request,
                "odj_list": odj_list,
                "odj_count": odj_count,
            }
            return templates.TemplateResponse(
                template, context
            )
        return PlainTextResponse(
            "You are banned - this is not your account..!"
        )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_details(
    request
):

    id = request.path_params["id"]
    template = "/admin/details.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            cmt_list = await item_comment(session, id)
            # ..
            detail = await in_item(session, id)
            # ..
            opt_service = await session.execute(
                select(Service)
                .join(Item.item_rent)
                .where(Service.service_belongs==id)
            )
            all_service = opt_service.scalars().unique()
            # ..
            opt_rent = await session.execute(
                select(Rent)
                .join(Item.item_rent)
                .where(Rent.rent_belongs==id)
            )
            all_rent = opt_rent.scalars().unique()
            # ..
            context = {
                "request": request,
                "detail": detail,
                "cmt_list": cmt_list,
                "all_service": all_service,
                "all_rent": all_rent,
            }
            return templates.TemplateResponse(
                template, context
            )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_create(
    request
):
    template = "/admin/create.html"
    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            owner_all = await all_user(session)
            # ..
            if admin:
                return templates.TemplateResponse(
                    template, {
                        "request": request,
                        "owner_all": owner_all,
                    }
                )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            item_owner = form["item_owner"]
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            # ..
            new = Item(f)
            new.title = title
            new.file = file
            new.item_owner = item_owner
            new.description = description
            # ..
            session.add(new)
            session.refresh(new)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/item/details/{ new.id }",
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
    template = "/admin/update.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        detail = await in_item(session, id)
        # ..
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if admin:
                return templates.TemplateResponse(
                    template, context
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            # ..
            file_query = (
                sqlalchemy_update(Item)
                .where(Item.id == id)
                .values(
                    file=file,
                    title=title,
                    description=description
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/item/details/{ detail.id }",
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
    template = "/admin/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            detail = await in_item(session, id)
            # ..
            if admin:
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
            # ..
            query = (
                delete(Item).where(Item.id == id)
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/admin/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()
