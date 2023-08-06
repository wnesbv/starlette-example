
from datetime import datetime

from sqlalchemy.future import select

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from starlette.responses import HTMLResponse

from starlette.authentication import requires
from starlette.templating import Jinja2Templates

from starlette.endpoints import WebSocketEndpoint
from channel_box import Channel, ChannelBox

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from channel.models import GroupChat, MessageChat, OneChat
from participant.models import PersonParticipant


templates = Jinja2Templates(directory="templates")


# ..One
class ChannelOne(WebSocketEndpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expires = 16000
        self.encoding = "json"


    async def on_connect(self, websocket):
        channel_name = websocket.query_params.get(
            "channel_name", "MySimpleChat"
        )
        await self.channel_get_or_create(channel_name, websocket)
        await websocket.accept()
        print(websocket['path'])


    async def on_receive(self, websocket, data):
        id_group = data["id_group"]
        name = websocket.user.user_id
        owner_msg = websocket.user.email
        message = data["message"]
        now_time = datetime.now().strftime(settings.TIME_FORMAT)

        async with async_session() as session:
            # ..
            stmt = await session.execute(
                select(PersonParticipant).where(
                    PersonParticipant.participant == name,
                    PersonParticipant.group_participant == id_group,
                )
            )
            odj_true = stmt.scalars().first()
            # ..
            stmt_admin = await session.execute(
                select(MessageChat)
                .join(GroupChat)
                .where(
                    MessageChat.id_group == id_group,
                    GroupChat.admin_group == name,
                )
            )
            odj_admin = stmt_admin.scalars().first()
            # ..
            if odj_admin or odj_true and message.strip():
                # ..
                payload = {
                    "name": name,
                    "owner_msg": owner_msg,
                    "message": message,
                    "now_time": now_time,
                }
                await self.channel_send(payload, history=True)
                # ..
                new = MessageChat()
                new.owner_msg = owner_msg
                new.message = message
                new.id_group = int(id_group)
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
        await engine.dispose()


# ..Two
class ChannelTwo(WebSocketEndpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expires = 16000
        self.encoding = "json"

    async def on_connect(self, websocket):
        channel_name = websocket.query_params.get(
            "channel_name", "MySimpleChat"
        )  # channel name */ws?channel_name=MySimpleChat

        await self.channel_get_or_create(channel_name, websocket)
        await websocket.accept()
        print(f" headers.. {websocket.headers['cookie']}")


    async def on_receive(self, websocket, data):
        message = data["message"]
        owner_msg = websocket.user.email

        async with async_session() as session:
            if message.strip():
                payload = {
                    "owner_msg": owner_msg,
                    "message": message,
                }
                await self.channel_send(payload, history=True)
                # ..
                new = OneChat()
                new.message = message
                new.owner_msg = owner_msg
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
        await engine.dispose()


# ..Two
class Chat(HTTPEndpoint):
    # ..
    @requires("authenticated", redirect="user_login")
    # ..
    async def get(self, request):
        template = "/chat/chat.html"
        async with async_session() as session:
            stmt = await session.execute(
                select(OneChat)
            )
            result = stmt.scalars().all()
            context = {
                "request": request,
                "result": result,
            }
            return templates.TemplateResponse(template, context)
        await engine.dispose()


class Message(HTTPEndpoint):
    async def get(self, request):
        await ChannelBox.channel_send(
            channel_name="MySimpleChat",
            payload={
                "username": "Message HTTPEndpoint",
                "message": "hello from Message",
            },
            history=True,
        )
        return JSONResponse({"message": "success"})


class Channels(HTTPEndpoint):
    async def get(self, request):
        channels = await ChannelBox.channels()
        return HTMLResponse(f"{channels}")


class ChannelsFlush(HTTPEndpoint):
    async def get(self, request):
        await ChannelBox.channels_flush()
        return JSONResponse({"flush": "success"})


class History(HTTPEndpoint):
    async def get(self, request):
        history = await ChannelBox.history()
        return HTMLResponse(f"{history}")


class HistoryFlush(HTTPEndpoint):
    async def get(self, request):
        await ChannelBox.history_flush()
        return JSONResponse({"flush": "success"})
