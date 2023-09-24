from pathlib import Path
from datetime import datetime

import aiofiles
import aiofiles.os

from sqlalchemy import insert, delete
from sqlalchemy.future import select

from aiocsv import AsyncWriter

from starlette.templating import Jinja2Templates
from starlette.responses import (
    PlainTextResponse,
    RedirectResponse,
)

from config.settings import BASE_DIR

from db_config.storage_config import engine, async_session
from options_select.opt_slc import for_id, id_and_owner

from auth_privileged.opt_slc import (
    privileged,
    get_privileged_user,
    sch_sv_service_owner_id,
    sch_sv_user,
    dump_schedule_service,
)
from .models import DumpService


templates = Jinja2Templates(directory="templates")


@privileged()
# ...
async def export_csv(request):
    # ..
    id = request.path_params["id"]
    # ..
    file_time = datetime.now()
    directory = (
        BASE_DIR / f"static/service/{file_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    )
    filename = f"{file_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv"

    async with async_session() as session:
        prv = await get_privileged_user(request, session)
        if request.method == "GET":
            # ..
            detail = await sch_sv_user(request, session, id)
            # ..
            if detail:
                # ..
                records = await sch_sv_service_owner_id(request, session, id)
                # ..
                async with aiofiles.open(
                    directory,
                    mode="w",
                    encoding="utf-8",
                ) as afp:
                    # ..
                    writer = AsyncWriter(afp)
                    # ..
                    await writer.writerow(
                        [
                            "id",
                            "name",
                            "title",
                            "description",
                            "type_on",
                            "number_on",
                            "there_is",
                            "created_at",
                            "owner",
                            "sch_s_service_id",
                        ]
                    )
                    for i in records:
                        await writer.writerow(
                            [
                                i.id,
                                i.name,
                                i.title,
                                i.description,
                                i.type_on.name,
                                i.number_on,
                                i.there_is,
                                i.created_at,
                                i.owner,
                                i.sch_s_service_id,
                            ]
                        )
                        # ..
                    # ..
                    title = file_time
                    query = insert(DumpService).values(
                        title=title,
                        owner=prv.id,
                        dump_s_service_id=id,
                    )
                    await session.execute(query)
                    await session.commit()
                    # ..
                    response = RedirectResponse(
                        f"/static/service/{filename}",
                        status_code=302,
                    )
                    return response
            return PlainTextResponse("You are banned - this is not your account..!")
    await engine.dispose()


@privileged()
# ...
async def dump_csv(request):
    # ..
    id = request.path_params["id"]
    template = "/schedule/dump_csv.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            obj_list = await dump_schedule_service(request, session, id)
            # ..
            if not obj_list:
                return PlainTextResponse("no information available..!")
                # ..
            context = {"request": request, "obj_list": obj_list}
            return templates.TemplateResponse(template, context)
    await engine.dispose()


@privileged()
# ...
async def delete_user_csv(request):
    # ..
    id = request.path_params["id"]
    template = "/schedule/delete_user_csv.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            detail = await id_and_owner(session, DumpService, request.user.user_id, id)
            # ..
            if detail:
                context = {"request": request}
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            result = await for_id(session, DumpService, id)
            root_directory = (
                BASE_DIR
                / f"static/service/{result.title.strftime('%Y-%m-%d-%H-%M-%S')}.csv"
            )
            await aiofiles.os.remove(root_directory)
            # ..
            query = delete(DumpService).where(DumpService.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/scheduleservice/list_service",
                status_code=303,
            )
            return response
    await engine.dispose()
