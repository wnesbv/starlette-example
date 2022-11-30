
from sqlalchemy import select, update as sqlalchemy_update, delete, func, asc, desc

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from mail.email import send_mail

from comment.models import Comment
from .opt_slc import in_admin


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def cmt_item_create(
    request
):
    template = "/comment/create.html"
    cmt_item_id = request.path_params["id"]
    cmt_user_id = request.user.display_name

    async with async_session() as session:
        #..
        admin = await in_admin(request, session)
        # ...
        if request.method == "GET":
            if admin:
                return templates.TemplateResponse(
                    template, {
                        "request": request,
                    }
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            opinion = form["opinion"]
            #..
            new_cmt = Comment()
            new_cmt.opinion = opinion
            new_cmt.cmt_user_id = cmt_user_id
            new_cmt.cmt_item_id = cmt_item_id

            session.add(new_cmt)
            session.refresh(new_cmt)
            await session.commit()

            await send_mail(
                f"A new object has been created - {cmt_user_id} - {cmt_item_id}: {opinion}"
            )

            response = RedirectResponse(
                f"/admin/item/details/{ cmt_item_id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_service_create(
    request
):
    template = "/comment/create.html"
    cmt_service_id = request.path_params["id"]
    cmt_user_id = request.user.display_name

    async with async_session() as session:
        #..
        admin = await in_admin(request, session)
        # ...
        if request.method == "GET":
            if admin:
                return templates.TemplateResponse(
                    template, {
                        "request": request,
                    }
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            opinion = form["opinion"]
            #..
            new_cmt = Comment()
            new_cmt.opinion = opinion
            new_cmt.cmt_user_id = cmt_user_id
            new_cmt.cmt_service_id = cmt_service_id

            session.add(new_cmt)
            session.refresh(new_cmt)
            await session.commit()

            await send_mail(
                f"A new object has been created - {cmt_user_id} - {cmt_service_id}: {opinion}"
            )

            response = RedirectResponse(
                f"/admin/service/details/{ cmt_service_id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_rent_create(
    request
):
    template = "/comment/create.html"
    cmt_rent_id = request.path_params["id"]
    cmt_user_id = request.user.display_name

    async with async_session() as session:
        #..
        admin = await in_admin(request, session)
        # ...
        if request.method == "GET":
            if admin:
                return templates.TemplateResponse(
                    template, {
                        "request": request,
                    }
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            opinion = form["opinion"]
            #..
            new_cmt = Comment()
            new_cmt.opinion = opinion
            new_cmt.cmt_user_id = cmt_user_id
            new_cmt.cmt_rent_id = cmt_rent_id

            session.add(new_cmt)
            session.refresh(new_cmt)
            await session.commit()

            await send_mail(
                f"A new object has been created - {cmt_user_id} - {cmt_rent_id}: {opinion}"
            )

            response = RedirectResponse(
                f"/admin/rent/details/{ cmt_rent_id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_item_update(
    request
):
    id = request.path_params["id"]
    template = "/comment/update.html"

    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(Comment)
            .where(Comment.id == id)
            .where(Comment.cmt_user_id == request.user.user_id)
        )
        detail = stmt.scalars().first()
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
            opinion = form["opinion"]
            #..
            query = (
                sqlalchemy_update(Comment)
                .where(Comment.id == id)
                .values(form)
                .execution_options(synchronize_session="fetch")
            )

            await session.execute(query)
            await session.commit()

            await send_mail(
                f"changes were made at the facility - {detail}: {opinion}"
            )

            response = RedirectResponse(
                f"/item/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_service_update(
    request
):
    id = request.path_params["id"]
    template = "/comment/update.html"

    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(Comment)
            .where(Comment.id == id)
            .where(Comment.cmt_user_id == request.user.user_id)
        )
        detail = stmt.scalars().first()
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
            opinion = form["opinion"]
            #..
            query = (
                sqlalchemy_update(Comment)
                .where(Comment.id == id)
                .values(form)
                .execution_options(synchronize_session="fetch")
            )

            await session.execute(query)
            await session.commit()

            await send_mail(
                f"changes were made at the facility - {detail}: {opinion}"
            )

            response = RedirectResponse(
                f"/item/service/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_rent_update(
    request
):
    id = request.path_params["id"]
    template = "/comment/update.html"

    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(Comment)
            .where(Comment.id == id)
            .where(Comment.cmt_user_id == request.user.user_id)
        )
        detail = stmt.scalars().first()
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
            opinion = form["opinion"]
            #..
            query = (
                sqlalchemy_update(Comment)
                .where(Comment.id == id)
                .values(form)
                .execution_options(synchronize_session="fetch")
            )

            await session.execute(query)
            await session.commit()

            await send_mail(
                f"changes were made at the facility - {detail}: {opinion}"
            )

            response = RedirectResponse(
                f"/item/rent/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()



@requires("authenticated", redirect="user_login")
# ...
async def cmt_delete(
    request
):
    id = request.path_params["id"]
    template = "/comment/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            result = await session.execute(
                select(Comment)
                .where(Comment.id == id)
                .where(Comment.cmt_user_id == request.user.user_id)
            )
            detail = result.scalars().first()
            #..
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
                delete(Comment).where(Comment.id == id)
            )
            #..
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()
