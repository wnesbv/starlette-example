
from datetime import datetime, date, timedelta

from passlib.hash import pbkdf2_sha1

from item.models import Slider

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
                        name="one",
                        email="one@example.com",
                        password=password_hash,
                        is_admin=True,
                        is_active=True,
                        email_verified=True,
                        created_at=datetime.now()
                    ),
                    User(
                        name="two",
                        email="two@example.com",
                        password=password_hash,
                        is_admin=False,
                        is_active=True,
                        email_verified=True,
                        created_at=datetime.now()
                    ),
                    GroupChat(
                        title="group one",
                        description="description group",
                        admin_group=1,
                        created_at=datetime.now()
                    ),
                    MessageChat(
                        message="message",
                        owner_msg=1,
                        id_group=1,
                        created_at=datetime.now()
                    ),
                    PersonParticipant(
                        explanations_person="one@example.com - explanations_person",
                        permission=0,
                        participant=2,
                        group_participant=1,
                        created_at=datetime.now()
                    ),
                    Item(
                        title="item 01 one",
                        description="description",
                        item_owner=1,
                        created_at=datetime.now()
                    ),
                    Item(
                        title="item 02 two",
                        description="description 02 two",
                        item_owner=2,
                        created_at=datetime.now()
                    ),
                    Rent(
                        title="rent 01",
                        description="description.. rent 01",
                        rent_owner=1,
                        rent_belongs=1,
                        created_at=datetime.now()
                    ),
                    Rent(
                        title="rent 02",
                        description="description.. rent 02",
                        rent_owner=1,
                        rent_belongs=1,
                        created_at=datetime.now()
                    ),
                    Service(
                        title="service 01",
                        description="description 01",
                        service_owner=1,
                        service_belongs=1,
                        created_at=datetime.now()
                    ),
                    Comment(
                        opinion="01 (one) item-opinion description",
                        user_on={"name": "one", "email": "one@example.com"},
                        cmt_user_id=1,
                        cmt_item_id=1,
                        created_at=datetime.now()
                    ),
                    Comment(
                        opinion="01 (one) service-opinion description",
                        user_on={"name": "one", "email": "one@example.com"},
                        cmt_user_id=1,
                        cmt_service_id=1,
                        created_at=datetime.now()
                    ),
                    Comment(
                        opinion="01 (one) rent-opinion description",
                        user_on={"name": "two", "email": "two@example.com"},
                        cmt_user_id=2,
                        cmt_rent_id=1,
                        created_at=datetime.now()
                    ),
                    ScheduleRent(
                        title="rent 01 ScheduleRent 01",
                        description="description.. rent 01 ScheduleRent 01",
                        sch_r_owner=1,
                        sch_r_rent_id=1,
                        created_at=datetime.now()
                    ),
                    ScheduleService(
                        name="name 01 Service 01",
                        title="service 01 ScheduleService 01",
                        description="description.. id-1 service 01 ScheduleService 01",
                        type_on="event",
                        number_on=date.today(),
                        there_is=datetime.now(),
                        sch_s_owner=1,
                        sch_s_service_id=1,
                        created_at=datetime.now()
                    ),
                    ScheduleService(
                        name="name 02 Service 01",
                        title="service 01 ScheduleService 02",
                        description="description.. id-2 service 01 ScheduleService 02",
                        type_on="birthday",
                        number_on=date.today(),
                        there_is=datetime.now() + timedelta(minutes=60),
                        sch_s_owner=1,
                        sch_s_service_id=1,
                        created_at=datetime.now()
                    ),
                    ReserveRentFor(
                        time_start=date.today(),
                        time_end=date.today() + timedelta(days=1),
                        rrf_owner=1,
                        rrf_item_id=1,
                        rrf_rent_id=1,
                        rrf_sch_r_id=1,
                        created_at=datetime.now()
                    ),
                    ReserveServicerFor(
                        reserve_time=datetime.now(),
                        rsf_owner=1,
                        rsf_service_id=1,
                        rsf_sch_s_id=1,
                        created_at=datetime.now()
                    ),
                    DumpService(
                        title=datetime.now(),
                        dump_s_owner=1,
                        dump_s_service_id=1,
                    ),
                    Slider(),
                ]
            )
            await session.flush()
        await session.commit()
    await engine.dispose()


async def on_app_shutdown() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
 #(event|holiday|birthday)
