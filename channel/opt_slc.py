import os, jwt, json, string, secrets, functools

from sqlalchemy import and_, or_, not_, true, false
from sqlalchemy.future import select

from participant.models import PersonParticipant
from collocutor.models import PersonCollocutor
from channel.models import GroupChat, MessageGroup

from auth_privileged.opt_slc import get_privileged_user

from .models import OneOneChat


async def prv_true(self, websocket, session):
    prv = await get_privileged_user(websocket, session)
    stmt = await session.execute(
        select(PersonParticipant).where(
            PersonParticipant.owner == prv.id,
            PersonParticipant.community == self.group_name,
        )
    )
    result = stmt.scalars().first()
    return result


async def user_true(self, websocket, session):
    stmt = await session.execute(
        select(PersonParticipant).where(
            PersonParticipant.owner == websocket.user.user_id,
            PersonParticipant.community == self.group_name,
        )
    )
    result = stmt.scalars().first()
    return result


async def prv_admin_true(self, websocket, session):
    prv = await get_privileged_user(websocket, session)
    stmt_admin = await session.execute(
        select(MessageGroup)
        .join(GroupChat)
        .where(
            MessageGroup.id_group == self.group_name,
            GroupChat.owner == prv.id,
        )
    )
    result = stmt_admin.scalars().first()
    return result


async def user_admin_true(self, websocket, session):
    stmt_admin = await session.execute(
        select(MessageGroup)
        .join(GroupChat)
        .where(
            MessageGroup.id_group == self.group_name,
            GroupChat.owner == websocket.user.user_id,
        )
    )
    result = stmt_admin.scalars().first()
    return result


async def in_obj_participant(session, obj, id):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.owner == obj,
                PersonParticipant.permission == false(),
                PersonParticipant.community == id,
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
                PersonParticipant.community == id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


# ..
async def prv_owner(self, websocket, session):
    prv = await get_privileged_user(websocket, session)
    stmt = await session.execute(
        select(PersonCollocutor).where(
            PersonCollocutor.owner == prv.id,
            PersonCollocutor.ref_num == self.group_name,
        )
    )
    result = stmt.scalars().first()
    return result


async def user_owner(self, websocket, session):
    stmt = await session.execute(
        select(PersonCollocutor).where(
            PersonCollocutor.owner == websocket.user.user_id,
            PersonCollocutor.ref_num == self.group_name,
        )
    )
    result = stmt.scalars().first()
    return result


async def prv_community(self, websocket, session):
    prv = await get_privileged_user(websocket, session)
    stmt = await session.execute(
        select(PersonCollocutor).where(
            PersonCollocutor.community == prv.id,
            PersonCollocutor.ref_num == self.group_name,
        )
    )
    result = stmt.scalars().first()
    return result


async def user_community(self, websocket, session):
    stmt = await session.execute(
        select(PersonCollocutor).where(
            PersonCollocutor.community == websocket.user.user_id,
            PersonCollocutor.ref_num == self.group_name,
        )
    )
    result = stmt.scalars().first()
    return result


# ..


async def group_ref_num(self, session):
    stmt = await session.execute(
        select(PersonCollocutor).where(
            PersonCollocutor.ref_num == self.group_name,
        )
    )
    result = stmt.scalars().first()
    return result


async def one_one_group(session, ref_num):
    stmt = await session.execute(
        select(OneOneChat)
        .join(PersonCollocutor.collocutor_one)
        .where(PersonCollocutor.ref_num == ref_num)
    )
    result = stmt.scalars().all()
    return result


async def one_one_select(session, ref_num, obj):
    stmt = await session.execute(
        select(OneOneChat)
        .join(PersonCollocutor.collocutor_one)
        .where(
            and_(
                or_(
                    PersonCollocutor.owner == obj,
                    PersonCollocutor.community == obj
                ),
                PersonCollocutor.ref_num == ref_num,
            )
        )
    )
    result = stmt.scalars().first()
    return result
