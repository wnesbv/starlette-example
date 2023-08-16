
from pathlib import Path

from sqlalchemy import select, update as sqlalchemy_update, delete

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from item.models import Slider

from .opt_slc import in_admin
from .opt_slider import all_count, all_slider, in_slider


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
root_directory = BASE_DIR / "static/upload"


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def slider_list(request):
    template = "/admin/slider/list.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            stmt = await session.execute(
                    select(Slider)
                    .order_by(Slider.id)
                )
            odj_list = stmt.scalars().all()
            # ..
            odj_count = await all_count(session)
            # ..
            context = {
                "request": request,
                "odj_list": odj_list,
                "odj_count": odj_count,
            }
            return templates.TemplateResponse(template, context)
        return PlainTextResponse("You are banned - this is not your account..!")
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def slider_details(request):

    id = request.path_params["id"]
    template = "/admin/slider/details.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        # ..
        if admin:
            # ..
            detail = await in_slider(request, session)
            # ..
            stmt = await session.execute(
                select(Slider)
                .where(
                    Slider.id == id,
                )
            )
            detail = stmt.scalars().first()
            context = {
                "request": request,
                "detail": detail,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


async def slider_create(request):

    template = "/admin/slider/create.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            odj_item = await all_slider(session)
            # ..
            if admin:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "odj_item": odj_item,
                    },
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
            new = Slider()
            new.title = title
            new.description = description
            new.file = file
            # ..
            session.add(new)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/slider/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def slider_update(request):

    id = request.path_params["id"]
    template = "/admin/slider/update.html"

    async with async_session() as session:
        # ..
        admin = await in_admin(request, session)
        detail = await in_slider(request, session)
        # ..
        context = {
            "request": request,
            "detail": detail,
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
            title = form["title"]
            description = form["description"]
            # ..
            query = (
                sqlalchemy_update(Slider)
                .where(Slider.id == id)
                .values(
                        title=title,
                        description=description
                    )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/slider/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def slider_file_update(
    request
):
    id = request.path_params["id"]
    template = "/admin/slider/update_file.html"

    async with async_session() as session:
        # ..
        detail = await in_slider(request, session)
        # ..
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
            file = form["file"]
            #..
            file_query = (
                sqlalchemy_update(Slider)
                .where(Slider.id == id)
                .values(
                    file=file,
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()
            #..
            response = RedirectResponse(
                f"/admin/slider/details/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def slider_delete(request):

    id = request.path_params["id"]
    template = "/admin/slider/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            admin = await in_admin(request, session)
            detail = await in_slider(request, session)
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
            query = delete(Slider).where(Slider.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/admin/slider/list",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def slider_file_delete(
    request
):

    id = request.path_params["id"]

    async with async_session() as session:

        if request.method == "GET":
            # ..
            detail = await in_slider(request, session)
            if detail:
                # ..
                root_directory = (
                    BASE_DIR
                    / f"static/upload/img/{detail.file.saved_filename}"
                )
                Path(root_directory).unlink()
                # ..
                file_query = (
                    sqlalchemy_update(Slider)
                    .where(Slider.id == id)
                    .values(
                        file=None,
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(file_query)
                await session.commit()
                # ..
                return RedirectResponse(
                    f"/admin/slider/details/{detail.id}",
                    status_code=302,
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
    await engine.dispose()
