
from pathlib import Path
from datetime import datetime

from sqlalchemy import update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from admin import img
from account.models import User

from options_select.opt_slc import (
    for_id,
    item_comment,
    and_owner_request,
    owner_request,
)

from options_select.csv_import import import_csv
from options_select.csv_export import export_csv

from auth_privileged.opt_slc import (
    get_privileged_user,
    privileged,
    owner_prv,
    get_owner_prv,
    id_and_owner_prv,
)

from .models import Item, Service, Rent
from config.settings import BASE_DIR

from .img import im_item
from .create_update import parent_create, child_img_create, child_img_update


templates = Jinja2Templates(directory="templates")


@privileged()
# ...
async def export_item_csv(request):
    async with async_session() as session:
        # ..
        if request.method == "GET":
            # ..
            prv = await get_privileged_user(request, session)
            result = await owner_prv(session, Item, prv)
            # ..
            await export_csv(result, prv)
            # ..
            user = prv.email
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
            return templates.TemplateResponse(
                template,
                {
                    "request": request,
                },
            )
        # ...
        if request.method == "POST":
            # ..
            prv = await get_privileged_user(request, session)
            # ..
            await import_csv(request, session, Item, prv)
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
    obj = await parent_create(request, Item, "item", im_item)
    return obj


@privileged()
# ...
async def item_update(request):
    # ..
    id = request.path_params["id"]
    obj = await child_img_update(request, Item, id, "item", im_item)
    return obj


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
        i = await for_id(session, Item, id)
        cmt_list = await item_comment(session, id)
        prv = await get_privileged_user(request, session)
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
                "prv": prv,
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
