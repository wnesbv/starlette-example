from pathlib import Path
from datetime import datetime

import json, time

from pydantic import parse_obj_as

from sqlalchemy.future import select
from starlette.templating import Jinja2Templates
from starlette.responses import (
    Response,
    JSONResponse,
    RedirectResponse,
    PlainTextResponse,
)

from sqlalchemy import update as sqlalchemy_update, delete

from admin import img
from account.models import User

from db_config.storage_config import engine, async_session
from item.models import Item, Rent, Service, ScheduleRent, ScheduleService
from options_select.opt_slc import for_id, id_and_owner

from .schemas import FormCreate, FormUpdate, ListItem


templates = Jinja2Templates(directory="templates")


# ...
async def item_create(request):
    # ..
    basewidth = 800
    template = "/item/create.html"

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
            created_at = datetime.now()
            owner = request.user.user_id
            # ..
            if file.filename == "":
                # ..
                obj = FormCreate(
                    title=title,
                    description=description,
                    created_at=created_at,
                    owner=owner,
                )
                new = Item(
                    **obj.dict(),
                )
                print(str(FormCreate.model_dump(obj)))
                # ..
                session.add(new)
                await session.commit()
                # ..
                return RedirectResponse(
                    f"/item/item/details/{ new.id }",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, owner)
            obj = FormCreate(
                title=title,
                description=description,
                created_at=created_at,
                owner=owner,
            )
            new = Item(**obj.dict())
            # ..
            session.add(new)
            await session.flush()
            new.file = await img.item_img_creat(file, email.email, new.id, basewidth)
            session.add(new)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/item/item/details/{ new.id }",
                status_code=302,
            )
    await engine.dispose()



# ...
async def item_update(request):
    # ..
    basewidth = 800
    id = request.path_params["id"]
    template = "/item/update.html"

    async with async_session() as session:
        # ..
        i = await id_and_owner(session, Item, request.user.user_id, id)
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
            modified_at = datetime.now()
            del_obj = form.get("del_bool")
            # ..
            if file.filename == "":
                obj = FormUpdate(
                    title=title,
                    description=description,
                    modified_at=modified_at,
                )
                print(str(FormUpdate.model_dump(obj)))
                query = (
                    sqlalchemy_update(Item)
                    .where(Item.id == id)
                    .values( obj.__dict__)
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
                    return RedirectResponse(
                        f"/item/item/details/{id}",
                        status_code=302,
                    )
                return RedirectResponse(
                    f"/item/item/details/{id}",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, i.owner)
            obj = FormUpdate(
                title=title,
                description=description,
                modified_at=modified_at,
            )
            file_query = (
                sqlalchemy_update(Item)
                .where(Item.id == id)
                .values(
                    obj.__dict__,
                )
                .values(
                    file=await img.item_img_creat(file, email.email, id, basewidth),
                )
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(file_query)
            await session.commit()
            # ..
            print(str(FormUpdate.model_dump(obj)))
            return RedirectResponse(
                f"/item/item/details/{id}",
                status_code=302,
            )
    await engine.dispose()


async def all_list(request):
    template = "/api/list.html"
    return templates.TemplateResponse(template, {"request": request})


async def item_list(request):
    async with async_session() as session:
        # ..
        if request.method == "GET":
            stmt = await session.execute(select(Item))
            result = stmt.scalars().all()
            # ..
            obj = [
                {
                    "id": i.id,
                    "title": i.title,
                    "description": i.description,
                    "file": i.file,
                    "created_at": i.created_at,
                    "modified_at": i.modified_at,
                    "owner": i.owner,
                }
                for i in result
            ]
            obj_list = ListItem(each_item=obj)
            return JSONResponse(str(obj_list.model_dump()))
    await engine.dispose()


# async def item_list(request):
#     async with async_session() as session:
#         # ..
#         if request.method == "GET":
#             stmt = await session.execute(select(Item))
#             obj_list = stmt.scalars().all()
#             # ..
#             start = time.time()
#             print(" start 1..")
#             obj = parse_obj_as(
#                 list[ListItem],
#                 [
#                     {
#                         "id": i.id,
#                         "title": i.title,
#                         "description": i.description,
#                         "file": i.file,
#                         "created_at": i.created_at,
#                         "modified_at": i.modified_at,
#                         "owner": i.owner,
#                     }
#                     for i in obj_list
#                 ],
#             )
#             to_return = json.dumps(obj, default=str)
#             end = time.time()
#             print(" end 1..", end - start)
#             return Response(to_return)
#     await engine.dispose()


# async def item_list(
#     request
# ):
#     async with async_session() as session:
#         #..
#         stmt = await session.execute(select(Item))
#         obj_list = stmt.scalars().all()
#         #..
#         obj = [
#             {
#                 "id": i.id,
#                 "title": i.title,
#                 "description": i.description,
#                 "file": i.file,
#                 "created_at": i.created_at,
#                 "modified_at": i.modified_at,
#                 "owner": i.owner,
#             }
#             for i in obj_list
#         ]
#         #return JSONResponse(obj)
#         to_return = json.dumps(obj, default=str)
#         return Response(to_return)
#     await engine.dispose()


async def item_details(request):
    # ..
    id = request.path_params["id"]
    # ..
    async with async_session() as session:
        # ..
        i = await for_id(session, Item, id)
        # ..
        obj = ListItem(
            id=i.id,
            title=i.title,
            description=i.description,
            file=i.file,
            created_at=i.created_at,
            modified_at=i.modified_at,
            owner=i.owner,
        )
        return JSONResponse(str(ListItem.model_dump(obj)))
    await engine.dispose()


# async def item_details(request):
#     id = request.path_params["id"]
#     async with async_session() as session:
#         # ..
#         stmt = await session.execute(select(Item).where(Item.id == id))
#         i = stmt.scalars().first()
#         # ..
#         obj = {
#             "id": i.id,
#             "title": i.title,
#             "description": i.description,
#             "file": i.file,
#             "created_at": i.created_at,
#             "modified_at": i.modified_at,
#             "owner": i.owner,
#         }
#         return JSONResponse(str(ListItem(**obj)))
#     await engine.dispose()


async def schedule_rent_list(request):
    async with async_session() as session:
        # ..
        stmt = await session.execute(
            select(ScheduleRent).join(Rent.rent_sch_r).order_by(ScheduleRent.id.desc())
        )
        obj_list = stmt.scalars().all()
        # ..
        obj = [
            {
                "id": to.id,
                "title": to.title,
                "start": to.start,
                "end": to.end,
            }
            for to in obj_list
        ]
        return Response(
            json.dumps(obj, default=str),
        )
    await engine.dispose()


async def schedule_service_list(request):
    async with async_session() as session:
        # ..
        stmt = await session.execute(
            select(ScheduleService)
            .join(Service.service_sch_s)
            .order_by(ScheduleService.id.desc())
        )
        obj_list = stmt.scalars().all()
        # ..
        obj = [
            {
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "number_on": i.number_on,
            }
            for i in obj_list
        ]
        return Response(
            json.dumps(obj, default=str),
        )
    await engine.dispose()
