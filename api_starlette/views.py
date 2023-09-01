import json, time

from pydantic import parse_obj_as

from sqlalchemy.future import select
from starlette.templating import Jinja2Templates
from starlette.responses import (
    Response,
    JSONResponse,
    # RedirectResponse,
    # PlainTextResponse,
)

from db_config.storage_config import engine, async_session
from item.models import Item, Rent, Service, ScheduleRent, ScheduleService
from api_starlette.schemas import ListItem


templates = Jinja2Templates(directory="templates")


async def all_list(request):
    template = "/api/list.html"
    return templates.TemplateResponse(template, {"request": request})


async def item_list(request):
    async with async_session() as session:
        # ..
        if request.method == "GET":
            stmt = await session.execute(select(Item))
            obj_list = stmt.scalars().all()
            # ..
            start = time.time()
            print(" start 1..")
            obj = parse_obj_as(
                list[ListItem],
                [
                    {
                        "id": i.id,
                        "title": i.title,
                        "description": i.description,
                        "file": i.file,
                        "created_at": i.created_at,
                        "modified_at": i.modified_at,
                        "item_owner": i.item_owner,
                    }
                    for i in obj_list
                ],
            )
            to_return = json.dumps(obj, default=str)
            end = time.time()
            print(" end 1..", end - start)
            return Response(to_return)
    await engine.dispose()


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
#                 "item_owner": i.item_owner,
#             }
#             for i in obj_list
#         ]
#         #return JSONResponse(obj)
#         to_return = json.dumps(obj, default=str)
#         return Response(to_return)
#     await engine.dispose()


async def item_details(request):
    id = request.path_params["id"]
    async with async_session() as session:
        # ..
        stmt = await session.execute(select(Item).where(Item.id == id))
        i = stmt.scalars().first()
        # ..
        obj = ListItem(
            id=i.id,
            title=i.title,
            description=i.description,
            file=i.file,
            created_at=i.created_at,
            modified_at=i.modified_at,
            item_owner=i.item_owner,
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
#             "item_owner": i.item_owner,
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
