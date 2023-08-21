
from pathlib import Path
from datetime import datetime

from sqlalchemy import select, update as sqlalchemy_update, delete

from starlette.authentication import requires
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from passlib.hash import pbkdf2_sha1

from strtobool import strtobool

from db_config.storage_config import engine, async_session

from account.models import User
from item.models import Item, Service, Rent
from options_select import file_img
from options_select.opt_slc import all_total

from .opt_slc import in_admin, in_user


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def i_list(request):
    template = "/admin/user/list.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            stmt = await session.execute(select(User).order_by(User.created_at.desc()))
            obj_list = stmt.scalars().all()
            obj_count = await all_total(session, User)
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

    id = request.path_params["id"]
    template = "/admin/user/details.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            i = await in_user(session, id)
            # ..
            opt_item = await session.execute(
                select(Item)
                .where(Item.item_owner == id)
            )
            all_item = opt_item.scalars().all()
            opt_service = await session.execute(
                select(Service)
                .where(Service.service_owner == id)
            )
            all_service = opt_service.scalars().unique()
            # ..
            opt_rent = await session.execute(
                select(Rent)
                .where(Rent.rent_owner == id)
            )
            all_rent = opt_rent.scalars().unique()
            # ...
            context = {
                "request": request,
                "i": i,
                "all_item": all_item,
                "all_service": all_service,
                "all_rent": all_rent,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_create(request):

    template = "/admin/user/create.html"
    mdl = "user"
    basewidth = 800

    async with async_session() as session:
        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            # ..
            if admin:
                return templates.TemplateResponse(template, {"request": request})
        # ...
        if request.method == "POST":
            form = await request.form()
            # ..
            name = form["name"]
            email = form["email"]
            password = pbkdf2_sha1.hash(form["password"])
            file = form["file"]
            #
            email_verified = form["email_verified"]
            is_active = form["is_active"]
            is_admin = form["is_admin"]
            # ..
            stmt_name = await session.execute(select(User).where(User.name == name))
            name_exist = stmt_name.scalars().first()
            stmt_email = await session.execute(select(User).where(User.email == email))
            email_exist = stmt_email.scalars().first()
            # ..

            if name_exist:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="name already registered..!",
                )
            if email_exist:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="email already registered..!",
                )
            if file.filename == "":
                new = User()
                new.name = name
                new.email = email
                new.password = password
                new.created_at = datetime.now()
                new.email_verified = strtobool(email_verified)
                new.is_active = strtobool(is_active)
                new.is_admin = strtobool(is_admin)
                # ..
                session.add(new)
                await session.commit()
                # ..
                return RedirectResponse(
                    f"/admin/user/details/{ new.id }",
                    status_code=302,
                )
            new = User()
            new.name = name
            new.email = email
            new.password = password
            new.file = await file_img.img_creat(request, file, mdl, basewidth)
            new.created_at = datetime.now()
            new.email_verified = strtobool(email_verified)
            new.is_active = strtobool(is_active)
            new.is_admin = strtobool(is_admin)
            # ..
            session.add(new)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/admin/user/details/{ new.id }",
                status_code=302,
            )

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_update(request):

    id = request.path_params["id"]
    template = "/admin/user/update.html"
    mdl = "user"
    basewidth = 800

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        i = await in_user(session, id)
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
            name = form["name"]
            email = form["email"]
            file = form["file"]
            del_obj = form.get("del_bool")
            #
            email_verified = form["email_verified"]
            is_active = form["is_active"]
            is_admin = form["is_admin"]
            # ..

            if file.filename == "":
                query = (
                    sqlalchemy_update(User)
                    .where(User.id == id)
                    .values(
                        name=name,
                        email=email,
                        file=i.file,
                        email_verified=strtobool(email_verified),
                        modified_at=datetime.now(),
                        is_active=strtobool(is_active),
                        is_admin=strtobool(is_admin),
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(query)
                await session.commit()

                if del_obj:
                    if Path(f".{i.file}").exists():
                        Path.unlink(f".{i.file}")

                    fle_not = (
                        sqlalchemy_update(User)
                        .where(User.id == id)
                        .values(file=None, modified_at=datetime.now())
                        .execution_options(synchronize_session="fetch")
                    )
                    await session.execute(fle_not)
                    await session.commit()
                    return RedirectResponse(
                        f"/admin/user/details/{ id }",
                        status_code=302,
                    )
                return RedirectResponse(
                    f"/admin/user/details/{ id }",
                    status_code=302,
                )

            query = (
                sqlalchemy_update(User)
                .where(User.id == id)
                .values(
                    name=name,
                    email=email,
                    file=await file_img.img_creat(request, file, mdl, basewidth),
                    email_verified=strtobool(email_verified),
                    modified_at=datetime.now(),
                    is_active=strtobool(is_active),
                    is_admin=strtobool(is_admin),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/admin/user/details/{ id }",
                status_code=302,
            )

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_update_password(request):

    id = request.path_params["id"]
    template = "/admin/user/update_password.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        context = {
            "request": request,
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
            password = pbkdf2_sha1.hash(form["password"])
            # ..

            query = (
                sqlalchemy_update(User)
                .where(User.id == id)
                .values(
                    password=password,
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/admin/user/details/{ id }",
                status_code=302,
            )

    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def i_delete(request):

    id = request.path_params["id"]
    template = "/admin/user/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            detail = await in_user(session, id)
            # ..
            if admin:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "detail": detail,
                    },
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            query = delete(User).where(User.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/admin/user/list",
                status_code=302,
            )
            return response
    await engine.dispose()
