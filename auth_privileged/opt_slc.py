
from pathlib import Path

import os, jwt, json, string, secrets, functools

from sqlalchemy import and_, or_, not_, true
from sqlalchemy.future import select

from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from account.models import User
from comment.models import Comment
from participant.models import PersonParticipant
from channel.models import GroupChat, MessageChat
from item.models import Item, Rent, Service, ScheduleRent, ScheduleService, DumpService

from .models import Privileged

from make_an_appointment.models import ReserveRentFor, ReserveServicerFor


key = settings.SECRET_KEY
algorithm = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES


async def get_random_string():
    alphabet = string.ascii_letters + string.digits
    prv_key = "".join(secrets.choice(alphabet) for i in range(32))
    return prv_key


# ...
async def get_token_privileged(request):
    if request.cookies.get("privileged"):
        token = request.cookies.get("privileged")
        if token:
            payload = jwt.decode(token, key, algorithm)
            prv_key = payload["prv_key"]
            return prv_key


async def get_privileged(request, session):
    token = await get_token_privileged(request)
    stmt = await session.execute(
        select(Privileged)
        .where(Privileged.prv_key == token)
    )
    result = stmt.scalars().first()
    return result


async def get_privileged_user(request, session):
    while True:
        prv = await get_privileged(request, session)
        if not prv:
            break
        stmt = await session.execute(
            select(User).where(and_(User.id == prv.prv_in, User.privileged, true()))
        )
        result = stmt.scalars().first()
        return result


def privileged():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *a, **ka):
            async with async_session() as session:
                user = await get_privileged_user(request, session)
            await engine.dispose()
            if user:
                return await func(request, *a, **ka)
            return RedirectResponse("/privileged/login")
        return wrapper
    return decorator
# ...


async def id_and_owner_prv(request, session, model, id):
    prv = await get_privileged_user(request, session)
    stmt = await session.execute(
        select(model).where(
            and_(
                model.id == id,
                model.owner == prv.id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def get_owner_prv(request, session, model):
    prv = await get_privileged_user(request, session)
    stmt = await session.execute(
        select(model).where(model.owner == prv.id)
    )
    result = stmt.scalars().all()
    return result


async def owner_prv(session, model, prv):
    stmt = await session.execute(
        select(model).where(model.owner == prv.id)
    )
    result = stmt.scalars().all()
    return result


# ..
async def sch_sv_service_owner_id(request, session, id):
    prv = await get_privileged_user(request, session)
    stmt = await session.execute(
        select(ScheduleService)
        .where(
            and_(
                ScheduleService.sch_s_service_id == id,
                ScheduleService.owner == prv.id,
            )
        )
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().all()
    return result

async def sch_sv_id(request, session, id):
    prv = await get_privileged_user(request, session)
    stmt = await session.execute(
        select(ScheduleService.id)
        .where(
            and_(
                ScheduleService.sch_s_service_id == id,
                ScheduleService.owner == prv.id,
            )
        )
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().all()
    return result

async def sch_sv_user(request, session, id):
    prv = await get_privileged_user(request, session)
    stmt = await session.execute(
        select(ScheduleService).where(
            and_(
                ScheduleService.sch_s_service_id == id,
                ScheduleService.owner == prv.id,
            )
        )
    )
    result = stmt.scalars().first()
    return result
# ..


async def dump_schedule_service(request, session, id):
    prv = await get_privileged_user(request, session)
    stmt = await session.execute(
        select(DumpService)
        .where(
            and_(
                DumpService.dump_s_service_id == id,
                DumpService.owner == prv.id,
            )
        )
        .order_by(DumpService.id.desc())
    )
    result = stmt.scalars().all()
    return result
