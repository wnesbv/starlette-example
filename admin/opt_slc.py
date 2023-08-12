
from sqlalchemy import select, func, true, and_

from starlette.templating import Jinja2Templates
from account.models import User
from comment.models import Comment

from item.models import Item, Rent, Service, ScheduleRent, ScheduleService


templates = Jinja2Templates(directory="templates")


async def all_count(
    session
):
    stmt = await session.execute(
        select(func.count(User.id))
    )
    result = stmt.scalars().all()
    return result


async def all_user(
    session
):
    stmt = await session.execute(
        select(User)
    )
    result = stmt.scalars().all()
    return result


async def all_item(
    session
):
    stmt = await session.execute(
        select(Item)
    )
    result = stmt.scalars().all()
    return result


async def all_service(
    session
):
    stmt = await session.execute(
        select(Service)
    )
    result = stmt.scalars().all()
    return result


async def all_rent(
    session
):
    stmt = await session.execute(
        select(Rent)
    )
    result = stmt.scalars().all()
    return result


async def all_schedule(
    session
):
    stmt = await session.execute(
        select(ScheduleService)
    )
    result = stmt.scalars().all()
    return result


async def in_admin(
    request, session
):
    stmt = await session.execute(
        select(User)
        .where(
            and_(
                User.id == request.user.user_id,
                User.is_admin, true()
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def in_user(
    session, id
):
    stmt = await session.execute(
        select(User)
        .where(
            User.id == id,
        )
    )
    result = stmt.scalars().first()
    return result


async def in_item(
    session, id
):
    stmt = await session.execute(
        select(Item)
        .where(
            Item.id == id,
        )
    )
    result = stmt.scalars().first()
    return result


async def in_service(
    session, id
):
    stmt = await session.execute(
        select(Service)
        .where(
            Service.id == id,
        )
    )
    result = stmt.scalars().first()
    return result


async def in_rent(
    session, id
):
    stmt = await session.execute(
        select(Rent)
        .where(
            Rent.id==id,
        )
    )
    result = stmt.scalars().first()
    return result


async def in_schedule_r(
    session, id
):
    stmt = await session.execute(
        select(ScheduleRent)
        .where(
            ScheduleRent.id == id,
        )
    )
    result = stmt.scalars().first()
    return result


async def in_schedule_sv(
    session, id
):
    stmt = await session.execute(
        select(ScheduleService)
        .where(
            ScheduleService.id == id,
        )
    )
    result = stmt.scalars().first()
    return result


async def item_comment(
    session, id
):
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_item_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result


async def service_comment(
    session, id
):
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_service_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result


async def rent_comment(
    session, id
):
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_rent_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result
