from datetime import datetime

from sqlalchemy import update as sqlalchemy_update, delete, func, asc, desc, and_
from sqlalchemy.future import select

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from mail.send import send_mail

from options_select.opt_slc import in_comment
from .models import Comment


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def cmt_item_create(request):

    id = request.path_params["id"]
    cmt_item_id = request.path_params["id"]
    cmt_user_id = request.user.user_id
    template = "/comment/create.html"

    async with async_session() as session:
        # ..
        user = await in_comment(request, session, id)
        # ...
        if request.method == "GET":
            if user:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                    },
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            opinion = form["opinion"]
            # ..
            new = Comment()
            new.opinion = opinion
            new.cmt_user_id = cmt_user_id
            new.cmt_item_id = cmt_item_id
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            await send_mail(
                f"A new object has been created - {cmt_user_id} - {cmt_item_id}: {opinion}"
            )
            # ..
            response = RedirectResponse(
                f"/item/details/{ cmt_item_id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_rent_create(request):
    id = request.path_params["id"]
    cmt_rent_id = request.path_params["id"]
    cmt_user_id = request.user.user_id
    template = "/comment/create.html"

    async with async_session() as session:
        # ..
        user = await in_comment(request, session, id)
        # ...
        if request.method == "GET":
            if user:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                    },
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            opinion = form["opinion"]
            # ..
            new = Comment()
            new.opinion = opinion
            new.cmt_user_id = cmt_user_id
            new.cmt_rent_id = cmt_rent_id
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            await send_mail(
                f"A new object has been created - {cmt_user_id} - {cmt_rent_id}: {opinion}"
            )
            # ..
            response = RedirectResponse(
                f"/item/rent/details/{ cmt_rent_id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_service_create(request):
    id = request.path_params["id"]
    cmt_service_id = request.path_params["id"]
    cmt_user_id = request.user.user_id
    template = "/comment/create.html"

    async with async_session() as session:
        # ..
        user = await in_comment(request, session, id)
        # ...
        if request.method == "GET":
            if user:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                    },
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            opinion = form["opinion"]
            # ..
            new = Comment()
            new.opinion = opinion
            new.cmt_user_id = cmt_user_id
            new.cmt_service_id = cmt_service_id
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            await send_mail(
                f"A new object has been created - {cmt_user_id} - {cmt_service_id}: {opinion}"
            )
            # ..
            response = RedirectResponse(
                f"/item/service/details/{ cmt_service_id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_item_update(request):
    id = request.path_params["id"]
    template = "/comment/update.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(
            select(Comment).where(
                and_(Comment.id == id, Comment.cmt_user_id == request.user.user_id)
            )
        )
        detail = stmt.scalars().first()
        # ..
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            opinion = form["opinion"]
            # ..
            query = (
                sqlalchemy_update(Comment)
                .where(Comment.id == id)
                .values(opinion=opinion, modified_at=datetime.now())
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            await send_mail(f"changes were made at the facility - {detail}: {opinion}")
            # ..
            response = RedirectResponse(
                f"/item/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_rent_update(request):
    id = request.path_params["id"]
    template = "/comment/update.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(
            select(Comment).where(
                and_(Comment.id == id, Comment.cmt_user_id == request.user.user_id)
            )
        )
        detail = stmt.scalars().first()
        # ..
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            opinion = form["opinion"]
            # ..
            query = (
                sqlalchemy_update(Comment)
                .where(Comment.id == id)
                .values(opinion=opinion, modified_at=datetime.now())
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            await send_mail(f"changes were made at the facility - {detail}: {opinion}")
            # ..
            response = RedirectResponse(
                f"/item/rent/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_service_update(request):
    id = request.path_params["id"]
    template = "/comment/update.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(
            select(Comment).where(
                and_(Comment.id == id, Comment.cmt_user_id == request.user.user_id)
            )
        )
        detail = stmt.scalars().first()
        # ..
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            opinion = form["opinion"]
            # ..
            query = (
                sqlalchemy_update(Comment)
                .where(Comment.id == id)
                .values(opinion=opinion, modified_at=datetime.now())
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            await send_mail(f"changes were made at the facility - {detail}: {opinion}")
            # ..
            response = RedirectResponse(
                f"/item/service/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def cmt_delete(request):
    id = request.path_params["id"]
    template = "/comment/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            result = await session.execute(
                select(Comment).where(
                    and_(Comment.id == id, Comment.cmt_user_id == request.user.user_id)
                )
            )
            detail = result.scalars().first()
            # ..
            if detail:
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
            query = delete(Comment).where(Comment.id == id)
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/",
                status_code=302,
            )
            return response
    await engine.dispose()
