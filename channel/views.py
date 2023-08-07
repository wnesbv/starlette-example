
from datetime import datetime
import json

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
        group_name = websocket.path_params["id"]
        print(" group_name..!", group_name)
        print(" websocket dict..", dict(websocket))

        if group_name:
            channel = Channel(websocket, expires=60*60, encoding="json")
            status = await ChannelBox.channel_add(group_name, channel)
            print(" status..", status)
        await websocket.accept()
        print("websocket path..", websocket['path'])


    async def on_receive(self, websocket, data):
        message = data["message"]
        print(" message..", message)
        name = websocket.user.user_id
        owner_msg = websocket.user.email
        #now_time = datetime.now().strftime(settings.TIME_FORMAT)

        group_name = websocket.path_params["id"]

        async with async_session() as session:
            # ..
            stmt = await session.execute(
                select(PersonParticipant).where(
                    PersonParticipant.participant == name,
                    PersonParticipant.group_participant == group_name,
                )
            )
            odj_true = stmt.scalars().first()
            # ..
            stmt_admin = await session.execute(
                select(MessageChat)
                .join(GroupChat)
                .where(
                    MessageChat.id_group == group_name,
                    GroupChat.admin_group == name,
                )
            )
            odj_admin = stmt_admin.scalars().first()
            # ..
            if odj_admin or odj_true and message.strip():
                # ..
                payload = {
                    "owner_msg": owner_msg,
                    "message": message,
                }

                await ChannelBox.group_send(group_name, payload, history=True)
                # ..
                new = MessageChat()
                new.owner_msg = owner_msg
                new.message = message
                new.id_group = int(group_name)
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
        group_name="MySimpleChat"
        if group_name:
            # define user channel
            channel = Channel(websocket, expires=60*60, encoding="json")
            status = await ChannelBox.channel_add(group_name, channel)
            print(" group_name..", group_name)
            print(" status..", status)
            # add user channel to named group

        await websocket.accept()
        print(" headers..", websocket.headers['cookie'])
        print(" websocket..", websocket['path'])



    async def on_receive(self, websocket, data):

        message = data["message"]
        owner_msg = websocket.user.email
        print(" owner_msg..", owner_msg)
        print(" message..", message)

        async with async_session() as session:
            if message.strip():
                payload = {
                    "owner_msg": owner_msg,
                    "message": message,
                }
                group_name="MySimpleChat"
                await ChannelBox.group_send(group_name, payload, history=True)
                # ..
                new = OneChat()
                new.message = message
                new.owner_msg = owner_msg
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
        await engine.dispose()


# ..
@requires("authenticated", redirect="user_login")
# ..
async def all_chat(request):

    if request.method == "GET":
        template = "/chat/chat.html"

        async with async_session() as session:
            stmt = await session.execute(
                select(OneChat)
            )
            result = stmt.scalars().all()
        await engine.dispose()

        context = {
            "request": request,
            "result": result,
        }
        return templates.TemplateResponse(template, context)


class Message(HTTPEndpoint):
    async def get(self, request):
        await ChannelBox.group_send(
            group_name="MySimpleChat",
            payload={
                "username": "Message HTTPEndpoint",
                "message": "hello from Message",
            },
            history=True,
        )
        return JSONResponse({"message": "success"})


class Groups(HTTPEndpoint):
    async def get(self, request):
        groups = await ChannelBox.groups()
        return HTMLResponse(f"{groups}")


class GroupsFlush(HTTPEndpoint):
    async def get(self, request):
        await ChannelBox.groups_flush()
        return JSONResponse({"flush": "success"})


class History(HTTPEndpoint):
    async def get(self, request):
        history = await ChannelBox.history()
        return HTMLResponse(f"{history}")


class HistoryFlush(HTTPEndpoint):
    async def get(self, request):
        await ChannelBox.history_flush()
        return JSONResponse({"flush": "success"})
