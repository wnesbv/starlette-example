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
from channel.models import GroupChat, MessageChat
from item.models import Item, Rent, Service, ScheduleRent, ScheduleService, DumpService

from auth_privileged.opt_slc import (
    get_privileged_user,
    privileged,
    owner_prv,
    get_owner_prv,
    id_and_owner_prv,
)


key = settings.SECRET_KEY
algorithm = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES


async def prv_true(self, websocket, session):
    prv = await get_privileged_user(websocket, session)
    stmt = await session.execute(
        select(PersonParticipant).where(
            PersonParticipant.owner == prv.id,
            PersonParticipant.group_participant == self.group_name,
        )
    )
    result = stmt.scalars().first()
    return result


async def user_true(self, websocket, session):
    stmt = await session.execute(
        select(PersonParticipant).where(
            PersonParticipant.owner == websocket.user.user_id,
            PersonParticipant.group_participant == self.group_name,
        )
    )
    result = stmt.scalars().first()
    return result


async def prv_admin_true(self, websocket, session):
    prv = await get_privileged_user(websocket, session)
    stmt_admin = await session.execute(
        select(MessageChat)
        .join(GroupChat)
        .where(
            MessageChat.id_group == self.group_name,
            GroupChat.owner == prv.id,
        )
    )
    result = stmt_admin.scalars().first()
    return result


async def user_admin_true(self, websocket, session):
    stmt_admin = await session.execute(
        select(MessageChat)
        .join(GroupChat)
        .where(
            MessageChat.id_group == self.group_name,
            GroupChat.owner == websocket.user.user_id,
        )
    )
    result = stmt_admin.scalars().first()
    return result


# ..


async def in_obj_participant(session, obj, id):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.owner == obj,
                PersonParticipant.permission == false(),
                PersonParticipant.group_participant == id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_obj_accepted(session, obj, id):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.owner == obj,
                PersonParticipant.permission,
                true(),
                PersonParticipant.group_participant == id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def person_participant(session, obj):
    stmt = await session.execute(
        select(GroupChat).where(
            GroupChat.owner == obj,
        )
    )
    result = stmt.scalars().first()
    return result


async def all_true(session, id):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.group_participant == id,
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
                PersonParticipant.group_participant == id,
                PersonParticipant.permission == false(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def stop_double(session, obj, id):
    stmt_admin = await session.execute(
        select(PersonParticipant)
        .where(
            PersonParticipant.group_participant == id,
            PersonParticipant.owner == obj,
        )
    )
    result = stmt_admin.scalars().first()
    return result
