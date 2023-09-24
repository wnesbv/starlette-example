from datetime import datetime

from sqlalchemy import update as sqlalchemy_update, delete
from sqlalchemy.future import select
from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from mail.send import send_mail

from options_select.opt_slc import for_id, id_and_owner, owner_request

from item.models import Service, ScheduleService
from .models import ReserveServicerFor


templates = Jinja2Templates(directory="templates")



# ...
async def create_reserve_service(request):
    # ..
    id = request.path_params["id"]
    service = request.path_params["service"]
    template = "/make_an_appointment/create_reserve_time.html"

    async with async_session() as session:
        # ..
        sch = await for_id(session, ScheduleService, id)
        # ..
        if request.method == "GET":
            # ..
            stmt = await session.execute(select(Service).where(Service.id == service))
            i = stmt.scalars().first()
            # ..
            there_is = sch.there_is
            # ..
            return templates.TemplateResponse(
                template,
                {
                    "request": request,
                    "i": i,
                    "sch": sch,
                    "there_is": there_is,
                },
            )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            description = form["description"]
            # ..
            owner = request.user.user_id
            reserve_time = sch.there_is
            rsf_service_id = service
            rsf_sch_s_id = id
            # ..
            new = ReserveServicerFor()
            new.owner = owner
            new.rsf_sch_s_id = rsf_sch_s_id
            new.rsf_service_id = rsf_service_id
            new.description = description
            new.reserve_time = reserve_time
            # ..
            session.add(new)
            await session.commit()
            # ..
            await send_mail(f"A new object has been created - {new}:")
            # ..
            response = RedirectResponse(
                f"/reserve/detail-service/{new.id}",
                status_code=302,
            )
            return response
    await engine.dispose()



# ...
async def reserve_list_service(request):
    # ..
    template = "make_an_appointment/list_service.html"
    async with async_session() as session:
        # ..
        obj_list = await owner_request(session, ReserveServicerFor, request.user.user_id)
        # ..
        if obj_list:
            context = {
                "request": request,
                "obj_list": obj_list,
            }
            return templates.TemplateResponse(template, context)
        return PlainTextResponse("This is not your account..!")
    await engine.dispose()



# ...
async def reserve_detail_service(request):
    # ..
    id = request.path_params["id"]
    template = "make_an_appointment/details_service.html"

    async with async_session() as session:
        # ..
        i = await id_and_owner(
            session, ReserveServicerFor, request.user.user_id, id
        )
        if i:
            context = {
                "request": request,
                "i": i,
            }
            return templates.TemplateResponse(template, context)
        return PlainTextResponse("This is not your account..!")
    await engine.dispose()



# ...
async def reserve_update_service(request):
    # ..
    id = request.path_params["id"]
    template = "/make_an_appointment/update_service.html"

    async with async_session() as session:
        # ..
        i = await id_and_owner(
            session, ReserveServicerFor, request.user.user_id, id
        )
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
            form = await request.form()
            # ..
            reserve = form["reserve_time"]
            description = form["description"]
            # ..
            reserve_time = datetime.strptime(reserve, settings.DATE_T)
            # ..
            query = (
                sqlalchemy_update(ReserveServicerFor)
                .where(ReserveServicerFor.id == id)
                .values(description=description, reserve_time=reserve_time)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()

            response = RedirectResponse(
                f"/reserve/detail-service/{ i.id }",
                status_code=302,
            )
            return response
    await engine.dispose()



# ...
async def delete_rsf(request):
    # ..
    id = request.path_params["id"]
    template = "/make_an_appointment/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await id_and_owner(
                session, ReserveServicerFor, request.user.user_id, id
            )
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
            query = delete(ReserveServicerFor).where(ReserveServicerFor.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/reserve/list",
                status_code=302,
            )
            return response
    await engine.dispose()
