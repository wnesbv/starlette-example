
import json

from sqlalchemy.future import select
from starlette.templating import Jinja2Templates
from starlette.responses import (
    Response,
    JSONResponse,
    #RedirectResponse,
    #PlainTextResponse,
)

from db_config.storage_config import engine, async_session
from item.models import Item, Rent, Service, ScheduleRent, ScheduleService

templates = Jinja2Templates(directory="templates")


async def item_list(
    request
):
    async with async_session() as session:
        #..
        stmt = await session.execute(select(Item))
        obj_list = stmt.scalars().all()
        #..
        obj = [
            {
                "id": to.id,
                "title": to.title,
                "description": to.description,
                "file": to.file,
                "created_at": to.created_at,
            }
            for to in obj_list
        ]
        #return JSONResponse(obj)

        return Response(
            json.dumps(obj, default=str),
        )

    await engine.dispose()


async def item_details(
    request
):
    id = request.path_params["id"]
    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(Item)
            .where(Item.id == id)
        )
        obj_list = stmt.scalars()
        #..
        obj = [
            {
                "id": to.id,
                "title": to.title,
                "description": to.description,
                "file": to.file,
            }
            for to in obj_list
        ]
        return JSONResponse(obj)
    await engine.dispose()


async def schedule_rent_list(
    request
):
    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(ScheduleRent)
            .join(Rent.rent_sch_r)
            .order_by(ScheduleRent.id.desc())
        )
        obj_list = stmt.scalars().all()
        #..
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


async def schedule_service_list(
    request
):
    async with async_session() as session:
        #..
        stmt = await session.execute(
            select(ScheduleService)
            .join(Service.service_sch_s)
            .order_by(ScheduleService.id.desc())
        )
        obj_list = stmt.scalars().all()
        #..
        obj = [
            {
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "dates": i.dates,
            }
            for i in obj_list
        ]
        return Response(
            json.dumps(obj, default=str),
        )
    await engine.dispose()
