
from datetime import datetime

import aiofiles
from aiocsv import AsyncDictReader

from sqlalchemy import delete

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from config.settings import BASE_DIR

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from auth_privileged.opt_slc import privileged, get_privileged_user, sch_sv_user, sch_sv_id
from .models import ScheduleService


root_directory = BASE_DIR / "static/upload"


templates = Jinja2Templates(directory="templates")


@privileged()
# ...
async def import_sch_csv(request):
    # ..
    id = request.path_params["id"]
    template = "/item/scheduleservice/import_csv.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            i = await sch_sv_user(request, session, id)
            if i:
                # ..
                context = {"request": request}

                return templates.TemplateResponse(
                    template, context
                )
            return PlainTextResponse(
                "You are banned - this is not your account..!"
            )
        # ...
        if request.method == "POST":
            # ..
            result = await sch_sv_id(request, session, id)
            # ..
            query = delete(ScheduleService).where(
                ScheduleService.id.in_(result),
            )
            await session.execute(query)
            #..
            inp = await request.form()
            uploaded_file = inp["filename"]
            filename = uploaded_file.filename
            directory = BASE_DIR / "static/service"
            #..
            async with aiofiles.open(
                f"{directory}/{filename}",
                mode="r",
                encoding="utf-8",
            ) as afp:
                # ..
                session.add_all(
                    [
                        ScheduleService(
                            **{
                                "id": int(new["id"]),
                                "name": new["name"],
                                "type_on": new["type_on"],
                                "title": new["title"],
                                "description": new["description"],
                                "number_on": datetime.strptime(
                                    new["number_on"], settings.DATE
                                ).date(),
                                "there_is": datetime.strptime(
                                    new["there_is"], settings.DATETIME_FORMAT
                                ),
                                "created_at": datetime.now(),
                                "owner": request.user.user_id,
                                "sch_s_service_id": id,
                            }
                        )
                        async for new in AsyncDictReader(afp)
                    ]
                )
                # ..
                await session.commit()
                # ..
                response = RedirectResponse(
                    "/item/scheduleservice/list_service",
                    status_code=302,
                )
                return response
    await engine.dispose()
