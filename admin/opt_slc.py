
import jwt, functools

from sqlalchemy import select, true, and_

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from account.models import User
from comment.models import Comment
from auth_privileged.models import Privileged
from item.models import Item, Rent, Service, ScheduleRent, ScheduleService

from db_config.settings import settings
from db_config.storage_config import engine, async_session

key = settings.SECRET_KEY
algorithm = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES

templates = Jinja2Templates(directory="templates")


# ..
async def get_token_privileged(request):
    if request.cookies.get("privileged"):
        token = request.cookies.get("privileged")
        if token:
            payload = jwt.decode(token, key, algorithm)
            prv_key = payload["prv_key"]
            return prv_key


async def get_privileged(request, session):
    token = await get_token_privileged(request)
    stmt = await session.execute(select(Privileged).where(Privileged.prv_key == token))
    result = stmt.scalars().first()
    return result


async def get_admin_user(request, session):
    while True:
        prv = await get_privileged(request, session)
        if not prv:
            break
        stmt = await session.execute(
            select(User)
            .where(User.id == prv.prv_in)
            .where(User.is_admin, true())
            .where(User.privileged, true())
        )
        result = stmt.scalars().first()
        return result


def admin():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *a, **ka):
            async with async_session() as session:
                user = await get_admin_user(request, session)
            await engine.dispose()
            if user:
                return await func(request, *a, **ka)
            return RedirectResponse("/privileged/login")
        return wrapper
    return decorator
# ..


async def all_user(session):
    stmt = await session.execute(select(User))
    result = stmt.scalars().all()
    return result


async def all_item(session):
    stmt = await session.execute(select(Item))
    result = stmt.scalars().all()
    return result


async def all_service(session):
    stmt = await session.execute(select(Service))
    result = stmt.scalars().all()
    return result


async def all_rent(session):
    stmt = await session.execute(select(Rent))
    result = stmt.scalars().all()
    return result


async def all_schedule(session):
    stmt = await session.execute(select(ScheduleService))
    result = stmt.scalars().all()
    return result


async def in_item(session, id):
    stmt = await session.execute(
        select(Item).where(
            Item.id == id,
        )
    )
    result = stmt.scalars().first()
    return result


async def in_service(session, id):
    stmt = await session.execute(
        select(Service).where(
            Service.id == id,
        )
    )
    result = stmt.scalars().first()
    return result


async def in_rent(session, id):
    stmt = await session.execute(
        select(Rent).where(
            Rent.id == id,
        )
    )
    result = stmt.scalars().first()
    return result


async def details_schedule_service(session, service):
    stmt = await session.execute(
        select(ScheduleService)
        .where(ScheduleService.sch_s_service_id == service)
        .order_by(ScheduleService.id.desc())
    )
    result = stmt.scalars().all()
    return result


async def admin_comment(session, id):
    stmt = await session.execute(
        select(Comment)
        .where(Comment.id == id).where(User.is_admin, true())
    )
    result = stmt.scalars().first()
    return result


async def item_comment(session, id):
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_item_id == id)
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


async def rent_comment(session, id):
    stmt = await session.execute(
        select(Comment)
        .where(Comment.cmt_rent_id == id)
        .order_by(Comment.created_at.desc())
    )
    result = stmt.scalars()
    return result
