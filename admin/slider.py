from datetime import datetime, timedelta
from pathlib import Path

import random, shutil

from sqlalchemy import select, update as sqlalchemy_update, delete

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from item.models import Slider

from config.settings import BASE_DIR
from options_select.opt_slc import all_total

from .opt_slc import admin, get_admin_user
from .opt_slider import all_slider, in_slider

from . import img


templates = Jinja2Templates(directory="templates")


@admin()
# ...
async def slider_list(request):
    template = "/admin/slider/list.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            # ..
            obj_list = await all_slider(session)
            # ..
            obj_count = await all_total(session, Slider)
            # ..
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
async def slider_details(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/slider/details.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        # ..
        if obj:
            # ..
            i = await in_slider(session, id)
            # ..
            context = {
                "request": request,
                "i": i,
            }
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@admin()
# ...
async def slider_create(request):
    template = "/admin/slider/create.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            # ..
            if obj:
                return templates.TemplateResponse(template, {"request": request})
        # ...
        if request.method == "POST":
            mdl = "slider"
            basewidth = 800
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            id_sl = random.randint(100, 999)
            # ..
            new = Slider()
            new.id_sl = id_sl
            new.title = title
            new.description = description
            new.file = await img.sl_img_creat(request, session, file, mdl, id_sl, basewidth)
            new.created_at = datetime.now()
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


@admin()
# ...
async def slider_update(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/slider/update.html"

    async with async_session() as session:
        # ..
        obj = await get_admin_user(request, session)
        detail = await in_slider(session, id)
        # ..
        context = {
            "request": request,
            "detail": detail,
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
            title = form["title"]
            description = form["description"]
            # ..
            query = (
                sqlalchemy_update(Slider)
                .where(Slider.id == id)
                .values(title=title, description=description)
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


@admin()
# ...
async def slider_file_update(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/slider/update_file.html"

    async with async_session() as session:
        # ..
        i = await in_slider(session, id)
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
            mdl = "slider"
            basewidth = 800
            # ..
            form = await request.form()
            file = form["file"]
            id_sl = i.id_sl
            # ..
            file_query = (
                sqlalchemy_update(Slider)
                .where(Slider.id == id)
                .values(
                    file=await img.sl_img_creat(request, file, mdl, id_sl, basewidth),
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(file_query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/admin/slider/details/{ i.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@admin()
# ...
async def slider_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/admin/slider/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj = await get_admin_user(request, session)
            detail = await in_slider(session, id)
            # ..
            if obj:
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
            i = await in_slider(session, id)
            directory = (
                BASE_DIR / f"static/upload/slider/{request.user.email}/{i.id_sl}"
            )
            shutil.rmtree(directory)
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


@admin()
# ...
async def slider_file_delete(request):
    # ..
    id = request.path_params["id"]

    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await in_slider(session, id)
            if i:
                if Path(f".{i.file}").exists():
                    Path.unlink(f".{i.file}")
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
                    f"/admin/slider/details/{i.id}",
                    status_code=302,
                )
            return PlainTextResponse("You are banned - this is not your account..!")
    await engine.dispose()
