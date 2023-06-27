
from sqlalchemy import select, update as sqlalchemy_update, delete

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from passlib.hash import pbkdf2_sha1

from strtobool import strtobool

from db_config.storage_config import engine, async_session

from account.models import User
from item.models import Item, Service, Rent
from .opt_slc import all_count, in_admin, in_user


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def item_list(
    request
):
    template = "/admin/user/list.html"

    async with async_session() as session:
        #..
        admin = await in_admin(request, session)
        #..
        if admin:
            stmt = await session.execute(
                select(User).order_by(User.created_at.desc())
            )
            odj_list = stmt.scalars().all()

            odj_count = await all_count(session)

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
    template = "/admin/user/details.html"

    async with async_session() as session:
        #..
        admin = await in_admin(request, session)
        #..
        if admin:
            detail = await in_user(request, session)
            #..
            opt_service = await session.execute(
                select(Service)
                .join(Item.item_rent)
                .where(Service.service_belongs==id)
            )
            all_service = opt_service.scalars().unique()
            #..
            opt_rent = await session.execute(
                select(Rent)
                .join(Item.item_rent)
                .where(Rent.rent_belongs==id)
            )
            all_rent = opt_rent.scalars().unique()
            #...
            context = {
                "request": request,
                "detail": detail,
                "all_service": all_service,
                "all_rent": all_rent,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def item_create(
    request
):
    template = "/admin/user/create.html"

    async with async_session() as session:
        if request.method == "GET":
            #..
            admin = await in_admin(request, session)
            #..
            if admin:
                return templates.TemplateResponse(
                    template, {"request": request,}
                )
        # ...
        if request.method == "POST":
            form = await request.form()
            #..
            name = form["name"]
            name = form["name"]
            email = form["email"]
            password = pbkdf2_sha1.hash(form["password"])
            #
            email_verified = form["email_verified"]
            is_active = form["is_active"]
            is_admin = form["is_admin"]
            #..
            new = User()
            new.name = name
            new.email = email
            new.password = password
            #
            new.email_verified = strtobool(email_verified)
            new.is_active = strtobool(is_active)
            new.is_admin = strtobool(is_admin)
            #..
            session.add(new)
            session.refresh(new)
            await session.commit()
            #..
            response = RedirectResponse(
                f"/admin/user/details/{ new.id }",
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
    template = "/admin/user/update.html"

    async with async_session() as session:
        #..
        admin = await in_admin(request, session)
        detail = await in_user(request, session)
        #..
        context = {
            "request": request,
            "detail": detail,
        }
        #...
        if request.method == "GET":
            if admin:
                return templates.TemplateResponse(
                    template, context
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        #...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            name = form["name"]
            email = form["email"]
            password = pbkdf2_sha1.hash(form["password"])
            #
            email_verified = form["email_verified"]
            is_active = form["is_active"]
            is_admin = form["is_admin"]
            #..
            query = (
                sqlalchemy_update(User)
                .where(User.id == id)
                .values(
                    name = name,
                    email=email,
                    password = password,
                    email_verified = strtobool(email_verified),
                    is_active = strtobool(is_active),
                    is_admin = strtobool(is_admin),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                f"/admin/user/details/{ detail.id }",
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
    template = "/admin/user/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            admin = await in_admin(request, session)
            detail = await in_user(request, session)
            #..
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
            #..
            query = (
                delete(User).where(User.id == id)
            )
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/admin/user/list",
                status_code=302,
            )
            return response
    await engine.dispose()
