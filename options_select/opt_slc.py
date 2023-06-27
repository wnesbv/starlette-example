
from sqlalchemy import func, and_
from sqlalchemy.future import select

from starlette.templating import Jinja2Templates

from comment.models import Comment
from participant.models import PersonParticipant
from channel.models import GroupChat, MessageChat
from item.models import Item, Rent, Service, ScheduleRent, ScheduleService, DumpService
from make_an_appointment.models import ReserveRentFor, ReserveServicerFor

from db_config.settings import settings


templates = Jinja2Templates(directory="templates")


async def user_tm(request, session):
    stmt = await session.execute(
        select(Item)
        .where(Item.item_owner == request.user.user_id)
    )
    result = stmt.scalars().all()
    return result


async def user_rt(request, session):
    stmt = await session.execute(
        select(Rent)
        .where(Rent.rent_owner == request.user.user_id)
    )
    result = stmt.scalars().all()
    return result


async def user_sv(request, session):
    stmt = await session.execute(
        select(Service)
        .where(Service.service_owner == request.user.user_id)
    )
    result = stmt.scalars().all()
    return result


#..
async def schedule_rent(request, session):
    stmt = await session.execute(
        select(ScheduleRent)
        .where(ScheduleRent.sch_r_owner == request.user.user_id)
        .order_by(ScheduleRent.id.desc())
    )
    result = stmt.scalars().all()
    return result


async def schedule_service_id(request, session):
    stmt = await session.execute(
        select(Service)
        .join(ScheduleService.sch_s_service)
        .where(ScheduleService.sch_s_owner == request.user.user_id)
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().unique()
    return result


async def schedule_service(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(ScheduleService)
        .where(
            and_(
                ScheduleService.sch_s_service_id == id,
                ScheduleService.sch_s_owner == request.user.user_id,
            )
        )
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().all()
    return result


async def details_schedule_rent(request, session):
    # ..
    stmt = await session.execute(
        select(ScheduleRent)
        .where(
            ScheduleRent.sch_r_owner==request.user.user_id
        )
        .order_by(ScheduleRent.id.desc())
    )
    result = stmt.scalars().all()
    return result


async def details_schedule_service(request, session):
    service = request.path_params["service"]
    # ..
    stmt = await session.execute(
        select(ScheduleService)
        .where(ScheduleService.sch_s_service_id == service)
        .where(ScheduleService.sch_s_owner == request.user.user_id)
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().all()
    return result


async def dump_schedule_service(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(DumpService)
        .where(
            and_(
                DumpService.dump_s_service_id == id,
                DumpService.dump_s_owner == request.user.user_id,
            )
        )
        .order_by(DumpService.id.desc())
    )
    result = stmt.scalars().all()
    return result


#..
async def sch_sv_user(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(ScheduleService)
        .where(
            and_(
                ScheduleService.sch_s_service_id == id,
                ScheduleService.sch_s_owner == request.user.user_id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def sch_sv_id(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(ScheduleService.id)
        .where(
            and_(
                ScheduleService.sch_s_service_id == id,
                ScheduleService.sch_s_owner == request.user.user_id,
            )
        )
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().all()
    return result


#..
async def in_rrf(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(ReserveRentFor).where(
            and_(
                ReserveRentFor.id == id,
                ReserveRentFor.rrf_owner == request.user.user_id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_rsf(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(ReserveServicerFor).where(
            and_(
                ReserveServicerFor.id == id,
                ReserveServicerFor.rsf_owner == request.user.user_id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_item(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Item)
        .where(
            and_(
                Item.id == id,
                Item.item_owner == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_rent(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Rent)
        .where(
            and_(
                Rent.id == id,
                Rent.rent_owner == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_service(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Service)
        .where(
            and_(
                Service.id == id,
                Service.service_owner == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_schedule_rent(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(ScheduleRent).where(
            and_(
                ScheduleRent.id == id,
                ScheduleRent.sch_r_owner == request.user.user_id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_schedule_service(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(ScheduleService)
        .where(
            and_(
                ScheduleService.id == id,
                ScheduleService.sch_s_owner == request.user.user_id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_dump(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(DumpService)
        .where(
            and_(
                DumpService.id == id,
                DumpService.dump_s_owner == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_comment(request, session):
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_user_id == request.user.user_id)
    )
    result = stmt.scalars().all()
    return result


# ..
async def in_group_chat(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(GroupChat)
        .where(
            and_(
                GroupChat.id == id,
                GroupChat.admin_group == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_chat(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(MessageChat)
        .where(
            and_(
                MessageChat.id == id,
                MessageChat.owner_chat == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


# ..
async def in_person_participant(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(PersonParticipant)
        .where(
            and_(
                PersonParticipant.id == id,
                PersonParticipant.participant == request.user.user_id
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def person_participant(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(PersonParticipant)
        .join(GroupChat)
        .where(
            and_(
                PersonParticipant.group_participant == id,
                GroupChat.admin_group == request.user.user_id
            )
        )
    )
    result = stmt.scalars().first()
    return result


#..
async def item_comment(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_item_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result


async def rent_comment(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_rent_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result


async def service_comment(request, session):
    id = request.path_params["id"]
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_service_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result


#..
async def period_item(rtf, session):
    time_start = rtf.time_start
    time_end = rtf.time_end
    #..
    rsv = await session.execute(
        select(Item.id)
        .join(ReserveRentFor.rrf_item)
    )
    rsv_list = rsv.scalars().all()
    # ..
    stmt = await session.execute(
        select(Item)
        .join(
            ReserveRentFor.rrf_item,
        )
        .where(Rent.id.in_(rsv_list))
        .where(func.datetime(ReserveRentFor.time_end) < time_start)
        .where(func.datetime(ReserveRentFor.time_start) < time_start)
        .where(func.datetime(ReserveRentFor.time_end) < time_end)
    )
    result = stmt.scalars().unique()
    # ..
    return result


async def not_period(session):
    # ..
    rsv = await session.execute(
        select(Item.id)
        .join(ReserveRentFor.rrf_item)
    )
    rsv_list = rsv.scalars().all()
    #..
    stmt = await session.execute(
        select(Item)
        .join(Rent.rent_item)
        .where(
            Item.id.not_in(rsv_list)
        )
    )
    result = stmt.scalars().unique()
    # ..
    return result
