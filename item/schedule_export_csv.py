
from pathlib import Path
from datetime import datetime

import aiofiles
import aiofiles.os

from sqlalchemy import insert, delete
from sqlalchemy.future import select

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
    schedule_srv,
    dump_schedule_service,
)

from .models import DumpService


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
root_directory = BASE_DIR / "static/upload"


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
            detail = await sch_sv_user(request, session, id)
            #..
            if detail:
                # ..
                records = await schedule_srv(request, session, id)
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
                            "type_on",
                            "title",
                            "description",
                            "number_on",
                            "there_is",
                            "created_at",
                            "sch_s_owner",
                            "sch_s_service_id",
                        ]
                    )
                    for i in records:
                        await writer.writerow(
                            [
                                i.id,
                                i.name,
                                i.type_on,
                                i.title,
                                i.description,
                                i.number_on,
                                i.there_is,
                                i.created_at,
                                i.sch_s_owner,
                                i.sch_s_service_id,
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

    id = request.path_params["id"]
    template = "/item/schedule/dump_csv.html"

    async with async_session() as session:

        if request.method == "GET":
            #..
            odj_list = await dump_schedule_service(request, session, id)
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
            detail = await in_dump(request, session, id)
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
                "/item/schedule-service/list_service",
                status_code=303,
            )
            return response
    await engine.dispose()
