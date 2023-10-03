
from pathlib import Path
from datetime import datetime

import random, shutil

from sqlalchemy import select, update as sqlalchemy_update, delete

from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from strtobool import strtobool

from passlib.hash import pbkdf2_sha1

from account.views import user_email, user_name
from account.models import User

from db_config.storage_config import engine, async_session
from item.models import Item, Service, Rent
from options_select.opt_slc import all_total, for_id

from .opt_slc import admin, get_admin_user
from . import img


templates = Jinja2Templates(directory="templates")


@admin()
# ...
async def i_list(request):
    template = "/admin/user/list.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
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


@admin()
# ...
async def i_details(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/user/details.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            i = await for_id(session, User, id)
            # ..
            opt_item = await session.execute(select(Item).where(Item.owner == id))
            all_item = opt_item.scalars().all()
            opt_service = await session.execute(
                select(Service).where(Service.owner == id)
            )
            all_service = opt_service.scalars().unique()
            # ..
            opt_rent = await session.execute(select(Rent).where(Rent.owner == id))
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


@admin()
# ...
async def i_create(request):
    # ..
    basewidth = 800
    template = "/admin/user/create.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            # ..
            if obj:
                return templates.TemplateResponse(template, {"request": request})
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            name = form["name"]
            email = form["email"]
            password = pbkdf2_sha1.hash(form["password"])
            file = form["file"]
            #
            email_verified = form["email_verified"]
            privileged = form["privileged"]
            is_active = form["is_active"]
            is_admin = form["is_admin"]
            # ..
            name_exist = await user_name(session, name)
            email_exist = await user_email(session, email)
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
                new.privileged = strtobool(privileged)
                new.is_active = strtobool(is_active)
                new.is_admin = strtobool(is_admin)
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
                # ..
                return RedirectResponse(
                    f"/admin/user/details/{ new.id }",
                    status_code=302,
                )
            # ..
            new = User()
            new.name = name
            new.email = email
            new.password = password
            new.file = await img.user_img_creat(file, email, basewidth)
            new.created_at = datetime.now()
            new.email_verified = strtobool(email_verified)
            new.is_active = strtobool(is_active)
            new.is_admin = strtobool(is_admin)
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/admin/user/details/{ new.id }",
                status_code=302,
            )

    await engine.dispose()


@admin()
# ...
async def i_update(request):
    # ..
    basewidth = 800
    id = request.path_params["id"]
    template = "/admin/user/update.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        i = await for_id(session, User, id)
        # ..
        context = {
            "request": request,
            "i": i,
        }
        # ...
        if request.method == "GET":
            if obj:
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
                        is_active=strtobool(is_active),
                        is_admin=strtobool(is_admin),
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
            # ..
            file_query = (
                sqlalchemy_update(User)
                .where(User.id == id)
                .values(
                    name=name,
                    email=email,
                    file=await img.user_img_creat(file, email, basewidth),
                    email_verified=strtobool(email_verified),
                    is_active=strtobool(is_active),
                    is_admin=strtobool(is_admin),
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/admin/user/details/{ id }",
                status_code=302,
            )

    await engine.dispose()


@admin()
# ...
async def i_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/user/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            i = await for_id(session, User, id)
            # ..
            if obj:
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
            i = await for_id(session, User, id)
            await img.del_user(i.email)
            # ..
            await session.delete(i)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/admin/user/list",
                status_code=302,
            )
            return response
    await engine.dispose()


@admin()
# ...
async def i_update_password(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/user/update_password.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        context = {
            "request": request,
        }
        # ...
        if request.method == "GET":
            if obj:
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
