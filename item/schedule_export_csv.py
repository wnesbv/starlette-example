
from pathlib import Path
from datetime import datetime

import aiofiles
import aiofiles.os
from sqlalchemy import select, insert, delete
from aiocsv import AsyncWriter

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import (
    PlainTextResponse,
    RedirectResponse,
)

from db_config.storage_config import engine, async_session
from options_select.opt_slc import (
    in_dump,
    sch_sv_user,
    schedule_service,
    dump_schedule_service,
)

from .models import DumpService
from .img import BASE_DIR


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def export_csv(request):

    id = request.path_params["id"]

    file_time = datetime.now()
    root_directory = (
        BASE_DIR
        / f"static/service/{file_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    )
    filename = f"{file_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv"

    async with async_session() as session:

        if request.method == "GET":
            #..
            detail = await sch_sv_user(request, session)
            #..
            if detail:
                # ..
                records = await schedule_service(request, session)
                # ..
                async with aiofiles.open(
                    root_directory, mode="w",
                    encoding="utf-8",
                ) as afp:
                    #..
                    writer = AsyncWriter(afp)
                    #..
                    await writer.writerow(
                        [
                            "id",
                            "name",
                            "type",
                            "title",
                            "description",
                            "date",
                            "there_is",
                            "created_at",
                            "sch_s_owner",
                            "sch_s_service_id",
                        ]
                    )
                    for item in records:
                        await writer.writerow(
                            [
                                item.id,
                                item.name,
                                item.type,
                                item.title,
                                item.description,
                                item.date,
                                item.there_is,
                                item.created_at,
                                item.sch_s_owner,
                                item.sch_s_service_id,
                            ]
                        )
                        # ..
                    #..
                    title = file_time
                    query = insert(DumpService).values(
                        title=title,
                        dump_s_owner=request.user.user_id,
                        dump_s_service_id=id,
                    )
                    await session.execute(query)
                    await session.commit()
                    #..
                    response = RedirectResponse(
                        f"/static/service/{filename}",
                        status_code=302,
                    )
                    return response
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def dump_csv(request):

    template = "/item/schedule/dump_csv.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            odj_list = await dump_schedule_service(request, session)
            #..
            if not odj_list:
                return PlainTextResponse(
                    "no information available..!"
                )
                #..
            context = {"request": request, "odj_list": odj_list}
            return templates.TemplateResponse(
                template, context
            )
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def delete_user_csv(request):

    id = request.path_params["id"]
    template = "/item/schedule/delete_user_csv.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            detail = await in_dump(request, session)
            #..
            if detail:
                context = {"request": request}
                return templates.TemplateResponse(
                    template, context
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            #..
            stmt = await session.execute(
                select(DumpService)
                .where(DumpService.id == id)
            )
            result = stmt.scalars().first()
            root_directory = (
                BASE_DIR
                / f"static/service/{result.title.strftime('%Y-%m-%d-%H-%M-%S')}.csv"
            )
            await aiofiles.os.remove(root_directory)
            #..
            query = (
                delete(DumpService)
                .where(DumpService.id == id)
            )
            await session.execute(query)
            await session.commit()
            #..
            response = RedirectResponse(
                "/item/schedule-service/list_id_service",
                status_code=303,
            )
            return response
    await engine.dispose()
