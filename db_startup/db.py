
import datetime

from passlib.hash import pbkdf2_sha1

from app import Slider

from comment.models import Comment
from account.models import User
from participant.models import PersonParticipant
from channel.models import GroupChat, MessageChat
from item.models import Item, Rent, Service, ScheduleService, ScheduleRent, DumpService
from make_an_appointment.models import ReserveRentFor, ReserveServicerFor


from db_config.storage_config import Base, engine, async_session


async def on_app_startup() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():

            password_hash = pbkdf2_sha1.hash("password")
            session.add_all(
                [
                    User(
                        name="User One",
                        email="one@example.com",
                        username="user-one",
                        password=password_hash,
                        is_admin=True,
                        is_active=True,
                        email_verified=True,
                    ),
                    User(
                        name="user two",
                        email="two@example.com",
                        username="two-user",
                        password=password_hash,
                        is_admin=False,
                        is_active=True,
                        email_verified=True,
                    ),
                    Comment(
                        opinion="01 (one) item-opinion description",
                        cmt_user_id=1,
                        cmt_item_id=1,
                    ),
                    Comment(
                        opinion="01 (one) service-opinion description",
                        cmt_user_id=1,
                        cmt_service_id=1,
                    ),
                    GroupChat(
                        title="group one",
                        description="description group",
                        admin_group=1,
                    ),
                    MessageChat(
                        message="message",
                        owner_chat=1,
                        id_group=1,
                    ),
                    PersonParticipant(
                        explanations_person="one@example.com - explanations_person",
                        permission=0,
                        participant=2,
                        group_participant=1,
                    ),
                    Item(
                        title="item 01 one",
                        description="description",
                        item_owner=1,
                    ),
                    Item(
                        title="item 02 two",
                        description="description 02 two",
                        item_owner=2,
                    ),
                    Rent(
                        title="rent 01",
                        description="description.. rent 01",
                        rent_owner=1,
                        rent_belongs=1,
                    ),
                    Rent(
                        title="rent 02",
                        description="description.. rent 02",
                        rent_owner=1,
                        rent_belongs=1,
                    ),
                    Service(
                        title="service 01",
                        description="description 01",
                        service_owner=1,
                        service_belongs=1,
                    ),
                    ScheduleRent(
                        title="rent 01 ScheduleRent 01",
                        description="description.. rent 01 ScheduleRent 01",
                        sch_r_owner=1,
                        sch_r_rent_id=1,
                        ),
                    ScheduleService(
                        name="name 01 Service 01",
                        type="event",
                        title="service 01 ScheduleService 01",
                        description="description.. id-1 service 01 ScheduleService 01",
                        sch_s_owner=1,
                        sch_s_service_id=1,
                        ),
                    ScheduleService(
                        name="name 02 Service 01",
                        type="event",
                        title="service 01 ScheduleService 02",
                        description="description.. id-2 service 01 ScheduleService 02",
                        sch_s_owner=1,
                        sch_s_service_id=1,
                        ),
                    ReserveRentFor(
                        time_start=datetime.date.today(),
                        time_end=datetime.date.today() + datetime.timedelta(days=1),
                        rrf_owner=1,
                        rrf_item_id=1,
                        rrf_rent_id=1,
                        rrf_sch_r_id=1,
                    ),
                    ReserveServicerFor(
                        reserve_time=datetime.datetime.now(),
                        rsf_owner=1,
                        rsf_service_id=1,
                        rsf_sch_s_id=1,
                    ),
                    DumpService(),
                    Slider()
                ]
            )
            await session.flush()
        await session.commit()
    await engine.dispose()


async def on_app_shutdown() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
 #(event|holiday|birthday)
