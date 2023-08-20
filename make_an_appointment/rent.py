from datetime import date, datetime, timedelta
import json, datetime as dtm
from sqlalchemy import insert, update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette import status
from starlette.exceptions import HTTPException
from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from options_select.opt_slc import (
    in_rrf,
    period_item,
    period_rent,
    not_period_item,
    not_period_rent,
)

from .models import ReserveRentFor


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def reserve_add(request):
    # ..
    template = "make_an_appointment/index.html"
    # ..
    if request.method == "GET":
        return templates.TemplateResponse(template, {"request": request})
    # ...
    if request.method == "POST":
        # ..
        form = await request.form()
        end = form["time_end"]
        start = form["time_start"]
        # ..
        if start >= end or start < date.today().strftime(settings.DATE):
            return PlainTextResponse("please enter proper dates")
        # ..
        payload = {
            "start": start,
            "end": end,
        }
        reserve = json.dumps(payload)
        # ..
        response = RedirectResponse(
            "/reserve/choice-item",
            status_code=302,
        )
        response.set_cookie("reserve", reserve)
        return response


async def get_token_reserve(request):
    if not request.cookies.get("reserve"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="not reserve token ..!",
        )
    token_get = request.cookies.get("reserve")
    token_loads = json.loads(token_get)
    return token_loads


# ..ITEM
@requires("authenticated", redirect="user_login")
# ...
async def reserve_choice_item(request):
    # ..
    token = await get_token_reserve(request)
    start = token["start"]
    end = token["end"]
    # ..
    time_start = datetime.strptime(start, settings.DATE)
    time_end = datetime.strptime(end, settings.DATE)
    reserve_period = [
        time_start + timedelta(days=x)
        for x in range(0, (time_end - time_start).days + 1)
    ]
    print(" reserve_period..", reserve_period)
    # ..
    rsv_period = []
    for period in reserve_period:
        rsv_period.append(period.strftime(settings.DATE))
    # ..
    rsv_period = str(rsv_period).replace("'", "").replace("[", "").replace("]", "")
    print(" rsv_period..", rsv_period)
    # ..
    template = "make_an_appointment/choice_item.html"

    async with async_session() as session:
        if request.method == "GET":
            if token:
                obj_list = await period_item(time_start, time_end, rsv_period, session)
                not_list = await not_period_item(session)

                context = {
                    "request": request,
                    "time_start": time_start,
                    "time_end": time_end,
                    "reserve_period": rsv_period,
                    "obj_list": obj_list,
                    "not_list": not_list,
                }

                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your token..!")
    await engine.dispose()


# ..RENT
@requires("authenticated", redirect="user_login")
# ...
async def reserve_choice_rent(request):
    # ..
    token = await get_token_reserve(request)
    start = token["start"]
    end = token["end"]
    # ..
    time_start = datetime.strptime(start, settings.DATE)
    time_end = datetime.strptime(end, settings.DATE)
    reserve_period = [
        time_start + timedelta(days=x)
        for x in range(0, (time_end - time_start).days + 1)
    ]
    # ..
    rsv_period = []
    for period in reserve_period:
        rsv_period.append(period.strftime(settings.DATE))
    rsv_period = str(rsv_period)
    # ..
    id = request.path_params["id"]
    template = "make_an_appointment/choice_rent.html"

    async with async_session() as session:
        if request.method == "GET":
            if token:
                obj_list = await period_rent(time_start, time_end, session)
                not_list = await not_period_rent(session, id)

                context = {
                    "request": request,
                    "time_start": time_start,
                    "time_end": time_end,
                    "reserve_period": str(rsv_period)
                    .replace("'", "")
                    .replace("[", "")
                    .replace("]", ""),
                    "obj_list": obj_list,
                    "not_list": not_list,
                }

                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your token..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            rrf_rent_id = form["rrf_rent_id"]
            # ..
            query = insert(ReserveRentFor).values(
                time_start=time_start,
                time_end=time_end,
                rrf_owner=request.user.user_id,
                rrf_item_id=id,
                rrf_rent_id=rrf_rent_id,
                created_at=datetime.now(),
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/item/rent/details/{ rrf_rent_id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def reserve_list_rent(request):
    # ..
    template = "make_an_appointment/list_rent.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(
            select(ReserveRentFor).where(
                ReserveRentFor.rrf_owner == request.user.user_id
            )
        )
        # ..
        obj_list = stmt.scalars().all()
        if obj_list:
            context = {
                "request": request,
                "obj_list": obj_list,
            }
            return templates.TemplateResponse(template, context)
        return PlainTextResponse("This is not your account..!")
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def reserve_detail_rent(request):
    # ..
    id = request.path_params["id"]
    template = "make_an_appointment/details_rent.html"

    async with async_session() as session:
        # ..
        obj = await in_rrf(request, session, id)
        if obj:
            context = {
                "request": request,
                "obj": obj,
            }
            return templates.TemplateResponse(template, context)
        return PlainTextResponse("This is not your account..!")
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def reserve_update_rent(request):
    # ..
    id = request.path_params["id"]
    template = "/make_an_appointment/update_rent.html"

    async with async_session() as session:
        # ..
        detail = await in_rrf(request, session, id)
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            form = await request.form()
            # ..
            end = form["time_end"]
            start = form["time_start"]
            description = form["description"]
            # ..
            time_end = datetime.strptime(end, settings.DATE)
            time_start = datetime.strptime(start, settings.DATE)
            # ..
            if start >= end or start < date.today().strftime(settings.DATE_POINT):
                return PlainTextResponse("please enter proper dates")
            # ..
            generated = [
                time_start + timedelta(days=x)
                for x in range(0, (time_end - time_start).days + 1)
            ]
            reserve_period = detail.reserve_period
            reserve_period = []
            for period in generated:
                reserve_period.append(period.strftime(settings.DATE))
            reserve_period = str(reserve_period)
            # ..
            query = (
                sqlalchemy_update(ReserveRentFor)
                .where(ReserveRentFor.id == id)
                .values(
                    time_end=time_end,
                    time_start=time_start,
                    description=description,
                    reserve_period=reserve_period,
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()

            response = RedirectResponse(
                f"/reserve/detail-rent/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def delete(request):
    # ..
    id = request.path_params["id"]
    template = "/make_an_appointment/delete.html"

    async with async_session() as session:
        # ...
        if request.method == "GET":
            # ..
            detail = await in_rrf(request, session, id)
            if detail:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "detail": detail,
                    },
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            query = delete(ReserveRentFor).where(ReserveRentFor.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()
