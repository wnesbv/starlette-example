
from sqlalchemy import select, func

from starlette.templating import Jinja2Templates

from item.models import Slider


templates = Jinja2Templates(directory="templates")


async def all_slider(
    session
):
    stmt = await session.execute(
        select(Slider)
    )
    result = stmt.scalars().all()
    return result


async def in_slider(
    session, id
):
    stmt = await session.execute(
        select(Slider)
        .where(
            Slider.id == id,
        )
    )
    result = stmt.scalars().first()
    return result
