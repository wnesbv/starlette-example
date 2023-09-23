from pathlib import Path

import os, jwt, json, string, secrets, functools

from sqlalchemy import and_, or_, not_, true, false
from sqlalchemy.future import select

from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from account.models import User
from comment.models import Comment
from participant.models import PersonParticipant
from channel.models import GroupChat, MessageGroup
from item.models import Item, Rent, Service, ScheduleRent, ScheduleService, DumpService

from auth_privileged.opt_slc import (
    get_privileged_user,
    privileged,
    owner_prv,
    get_owner_prv,
    id_and_owner_prv,
)


async def person_participant(session, model, obj):
    stmt = await session.execute(
        select(model).where(
            model.owner == obj,
        )
    )
    result = stmt.scalars().first()
    return result


async def all_true(session, id):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.community == id,
                PersonParticipant.permission,
                true(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def all_false(session, id):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.community == id,
                PersonParticipant.permission == false(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def stop_double(session, model, obj, id):
    stmt_admin = await session.execute(
        select(model)
        .where(
            model.community == id,
            model.owner == obj,
        )
    )
    result = stmt_admin.scalars().first()
    return result
