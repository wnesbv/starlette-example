
from pathlib import Path

import random, shutil

from sqlalchemy import func, and_, or_, not_
from sqlalchemy.future import select

from account.models import User
from comment.models import Comment
from participant.models import PersonParticipant
from channel.models import GroupChat, MessageChat
from item.models import Item, Rent, Service, ScheduleRent, ScheduleService, DumpService

from make_an_appointment.models import ReserveRentFor, ReserveServicerFor

from config.settings import BASE_DIR


async def all_total(session, model):
    stmt = await session.execute(select(func.count(model.id)))
    result = stmt.scalars().all()
    return result


async def for_id(session, model, id):
    stmt = await session.execute(
        select(model)
        .where(model.id == id)
    )
    result = stmt.scalars().first()
    return result


async def and_owner_request(request, session, model, id):
    stmt = await session.execute(
        select(model).where(
            and_(
                model.id == id,
                model.owner == request.user.user_id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def owner_request(request, session, model):
    stmt = await session.execute(
        select(model).where(model.owner == request.user.user_id)
    )
    result = stmt.scalars().all()
    return result

# ..
async def in_person_participant(request, session, id):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.id == id,
                PersonParticipant.owner == request.user.user_id,
            )
        )
    )
    result = stmt.scalars().all()
    return result


# ..
async def schedule_rent_user(request, session):
    stmt = await session.execute(
        select(ScheduleRent)
        .where(ScheduleRent.owner == request.user.user_id)
        .order_by(ScheduleRent.id.desc())
    )
    result = stmt.scalars().all()
    return result


async def srv_sch_user(request, session):
    stmt = await session.execute(
        select(Service)
        .join(ScheduleService.sch_s_service)
        .where(ScheduleService.owner == request.user.user_id)
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().unique()
    return result


async def schedule_sv(request, session, id):
    stmt = await session.execute(
        select(ScheduleService)
        .where(
            and_(
                ScheduleService.sch_s_service_id == id,
                ScheduleService.owner == request.user.user_id,
            )
        )
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().all()
    return result


async def details_schedule_rent(request, session):
    stmt = await session.execute(
        select(ScheduleRent)
        .where(ScheduleRent.owner == request.user.user_id)
        .order_by(ScheduleRent.id.desc())
    )
    result = stmt.scalars().all()
    return result


async def details_schedule_service(request, session, service):
    stmt = await session.execute(
        select(ScheduleService)
        .where(ScheduleService.sch_s_service_id == service)
        .where(ScheduleService.owner == request.user.user_id)
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().all()
    return result


async def dump_schedule_service(request, session, id):
    stmt = await session.execute(
        select(DumpService)
        .where(
            and_(
                DumpService.dump_s_service_id == id,
                DumpService.owner == request.user.user_id,
            )
        )
        .order_by(DumpService.id.desc())
    )
    result = stmt.scalars().all()
    return result


# ..
async def sch_sv_user(request, session, id):
    stmt = await session.execute(
        select(ScheduleService).where(
            and_(
                ScheduleService.sch_s_service_id == id,
                ScheduleService.owner == request.user.user_id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def sch_sv_id(request, session, id):
    stmt = await session.execute(
        select(ScheduleService.id)
        .where(
            and_(
                ScheduleService.sch_s_service_id == id,
                ScheduleService.owner == request.user.user_id,
            )
        )
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().all()
    return result


# ..
async def person_participant(request, session, id):
    stmt = await session.execute(
        select(PersonParticipant)
        .join(GroupChat)
        .where(
            and_(
                PersonParticipant.group_participant == id,
                GroupChat.owner == request.user.user_id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


# ..
async def item_comment(session, id):
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_item_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result


async def rent_comment(session, id):
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_rent_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result


async def service_comment(session, id):
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_service_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result


# ...tm
async def period_item(time_start, time_end, session):
    # ..
    stmt = await session.execute(select(Item.id).join(ReserveRentFor.rrf_item))
    result = stmt.scalars().all()
    # ..
    i = await session.execute(select(ReserveRentFor.time_start))
    start = i.scalars().all()
    # ..
    i = await session.execute(select(ReserveRentFor.time_end))
    end = i.scalars().all()
    # ..
    stmt = await session.execute(
        select(Item)
        .join(
            ReserveRentFor.rrf_item,
        )
        .where(Item.id.in_(result))
        .where(func.date(time_start).not_in(start))
        .where(func.date(time_end).not_in(end))
    )
    result = stmt.scalars().unique()
    # ..
    return result



async def period_rent(time_start, time_end, session):
    # ..
    stmt = await session.execute(
        select(Rent.id).join(ReserveRentFor.rrf_rent)
    )
    result = stmt.scalars().all()
    # ..
    i = await session.execute(select(ReserveRentFor.time_start))
    start = i.scalars().all()
    # ..
    i = await session.execute(select(ReserveRentFor.time_end))
    end = i.scalars().all()
    # ..
    stmt = await session.execute(
        select(Rent)
        .join(
            ReserveRentFor.rrf_rent,
        )
        .where(Rent.id.in_(result))
        .where(func.date(time_start).not_in(start))
        .where(func.date(time_end).not_in(end))
    )
    result = stmt.scalars().unique()
    # ..
    return result


async def not_period_item(session):
    # ..
    stmt = await session.execute(select(Item.id).join(ReserveRentFor.rrf_item))
    result = stmt.scalars().all()
    # ..
    stmt = await session.execute(select(Item).where(Item.id.not_in(result)))
    result = stmt.scalars().unique()
    # ..
    return result


async def not_period_rent(session, id):
    # ..
    stmt = await session.execute(
        select(Rent.id)
        .join(ReserveRentFor.rrf_rent)
    )
    result = stmt.scalars().all()
    # ..
    stmt = await session.execute(
        select(Rent)
        .where(Rent.id.not_in(result))
        .where(Rent.rent_belongs == id)
    )
    result = stmt.scalars().unique()
    # ..
    return result


async def id_fle_delete(request, mdl, id_fle):
    # ..
    directory = (
        BASE_DIR
        / f"static/upload/{mdl}/{request.user.email}/{id_fle}"
    )
    if Path(directory).exists():
        result = shutil.rmtree(directory)
        return result
