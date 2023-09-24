
from pathlib import Path
from datetime import datetime
import json

from sqlalchemy import update as sqlalchemy_update, delete, and_
from sqlalchemy.future import select
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from admin import img
from mail.send import send_mail
from account.models import User

from make_an_appointment.models import ReserveServicerFor

from .models import Item, Service, ScheduleService

from options_select.opt_slc import (
    for_id,
    service_comment,
    id_and_owner,
)
from auth_privileged.opt_slc import get_privileged_user, privileged, owner_prv

from .img import im_service
from .create_update import child_img_create, child_img_update


templates = Jinja2Templates(directory="templates")


@privileged()
# ...
async def service_create(request):
    # ..
    form = await request.form()
    belongs = form.get("belongs")
    new = Service()
    new.service_belongs = belongs
    # ..
    obj = await child_img_create(
        request, form, belongs, Item, new, "service", "item", im_service
    )
    return obj


@privileged()
# ...
async def service_update(request):
    # ..
    id = request.path_params["id"]
    obj = await child_img_update(
        request, Service, id, "service", im_service
    )
    return obj


@privileged()
# ...
async def service_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/service/delete.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            i = await id_and_owner(session, Service, request.user.user_id, id)
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
            i = await id_and_owner(session, Service, request.user.user_id, id)
            email = await for_id(session, User, i.owner)
            # ..
            await img.del_service(
                email.email, i.service_belongs, id
            )
            # ..
            await session.delete(i)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/service/list",
                status_code=302,
            )
            return response
    await engine.dispose()


async def service_list(request):
    # ..
    template = "/service/list.html"

    async with async_session() as session:
        # ..
        result = await session.execute(
            select(Service)
            .order_by(Service.id)
        )
        obj_list = result.scalars().all()
        # ..
        context = {
            "request": request,
            "obj_list": obj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def service_details(request):
    # ..
    id = request.path_params["id"]
    template = "/service/details.html"

    async with async_session() as session:
        # ..
        cmt_list = await service_comment(session, id)
        # ..
        i = await for_id(session, Service, id)
        #..
        rsv = await session.execute(
            select(ScheduleService.id)
            .join(ReserveServicerFor.rsf_sch_s)
            .where(
                ScheduleService.sch_s_service_id == id,
            )
        )
        rsv_list = rsv.scalars().all()
        #..
        stmt = await session.execute(
            select(ScheduleService)
            .where(
                and_(
                    ScheduleService.id.not_in(rsv_list),
                    ScheduleService.sch_s_service_id == id,
                )
            )
        )
        obj_list = stmt.scalars().all()
        # ..
        obj = [
            {
                "id": i.id,
                "name": i.name,
                "type_on": i.type_on,
                "number_on": i.number_on,
                "there_is": i.there_is.strftime("%H:%M"),
                "description": i.description,
            }
            for i in obj_list
        ]
        sch_json = json.dumps(obj, default=str)
        # ..
        context = {
            "request": request,
            "i": i,
            "cmt_list": cmt_list,
            "sch_json": sch_json,
        }

        return templates.TemplateResponse(template, context)
    await engine.dispose()
