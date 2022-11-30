
from datetime import datetime

from sqlalchemy import select

from starlette.templating import Jinja2Templates
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from channel_box import channel_box
from channel_box import ChannelBoxEndpoint

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from channel.models import GroupChat, MessageChat
from participant.models import PersonParticipant


templates = Jinja2Templates(directory="templates")


class ChatChannel(ChannelBoxEndpoint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expires = 1600
        self.encoding = "json"

    async def on_connect(self, websocket):
        channel_name = websocket.query_params.get(
            "channel_name", "MySimpleChat"
        )
        await self.channel_get_or_create(
            channel_name, websocket
        )
        await websocket.accept()


    async def on_receive(
        self,
        websocket,
        data
    ):
        id_group = data["id_group"]
        username = data["username"]
        message = data["message"]
        now_time = datetime.now().strftime(settings.TIME_FORMAT)
        #...
        async with async_session() as session:
            #..
            stmt = await session.execute(
                select(PersonParticipant)
                .where(
                    PersonParticipant.participant == username,
                    PersonParticipant.group_participant == id_group,
                )
            )
            odj_true = stmt.scalars().first()
            #..
            stmt_admin = await session.execute(
                select(MessageChat)
                .join(GroupChat)
                .where(
                    MessageChat.id_group == id_group,
                    GroupChat.admin_group == username,
                )
            )
            odj_admin = stmt_admin.scalars().first()
            #..
            if odj_admin or odj_true and message.strip():
                # ..
                payload = {
                    "username": username,
                    "message": message,
                    "now_time": now_time,
                }
                await self.channel_send(payload)
                # ..
                owner_chat = int(username)
                # ..
                new = MessageChat()
                new.username = username
                new.message = message
                new.owner_chat = owner_chat
                new.id_group = int(id_group)
                # ..
                session.add(new)
                await session.commit()
        await engine.dispose()


class SendFromAnotherPartOfCode(HTTPEndpoint):
    async def get(self, request):
        # you can catch requests from RabbitMQ for example
        await channel_box.channel_send(
            "MySimpleChat",
            {
                "username": "username",
                "message": "hello from SendFromAnotherPartCode",
            }
        )

        return JSONResponse({"SendFromAnotherPartOfCode": "success"})


class Flush(HTTPEndpoint):
    async def get(self, request):
        await channel_box.channels_flush()
        return JSONResponse({"Flush": "success"})
