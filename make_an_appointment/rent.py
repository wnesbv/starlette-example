
from datetime import date, datetime, timedelta

from sqlalchemy import insert, update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from options_select.opt_slc import in_rrf, period_item, not_period

from .models import ReserveRentFor


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def reserve_add(request):

    template = "make_an_appointment/index.html"

    async with async_session() as session:
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
            time_start = datetime.strptime(start, settings.DATE_T)
            time_end = datetime.strptime(end, settings.DATE_T)
            # ..
            if start >= end or start < date.today().strftime(settings.DATE):
                return PlainTextResponse("please enter proper dates")
            # ...
            generated = [
                time_start + timedelta(days=x)
                for x in range(0, (time_end - time_start).days + 1)
            ]

            reserve_period = []
            for period in generated:
                reserve_period.append(period.strftime(settings.DATE))

            reserve_period = str(reserve_period)

            # ..
            rrf_owner = request.user.user_id
            rrf_item_id = 1
            # ..
            new = ReserveRentFor()
            new.time_end = time_end
            new.time_start = time_start
            new.rrf_owner = rrf_owner
            new.reserve_period = reserve_period
            new.rrf_item_id = rrf_item_id
            # ..
            session.add(new)
            session.refresh(new)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/reserve/choice/{new.id}/",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def reserve_choice(request):

    id = request.path_params["id"]
    template = "make_an_appointment/choice.html"

    async with async_session() as session:

        if request.method == "GET":
            # ..
            rrf = await in_rrf(request, session, id)
            if rrf:
                # ..
                obj_item = await period_item(rrf, session)
                not_item = await not_period(session)

                reserve_period = rrf.reserve_period
                context = {
                    "request": request,
                    "rrf": rrf,
                    "not_item": not_item,
                    "obj_item": obj_item,
                    "reserve_period": reserve_period,
                }
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            rrf_item_id = form["rrf_item_id"]
            # ..
            time_start = rrf.time_start
            time_end = rrf.time_end
            rrf_owner = request.user.user_id
            # ..
            query = insert(ReserveRentFor).values(
                rrf_owner=rrf_owner,
                rrf_item_id=rrf_item_id,
                time_start=time_start,
                time_end=time_end,
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/item/details/{ rrf_item_id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def reserve_list_rent(request):

    template = "make_an_appointment/list_rent.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(
            select(ReserveRentFor)
            .where(ReserveRentFor.rrf_owner == request.user.user_id)
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
            query = (
                delete(ReserveRentFor)
                .where(ReserveRentFor.id == id)
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()
