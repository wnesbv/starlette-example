
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
        self.channel = None
        self.group_name = None

    async def on_connect(self, websocket):

        self.group_name = websocket.path_params["id"]
        print(" group_name..!", self.group_name)
        print(" websocket dict..", dict(websocket))

        if self.group_name:
            self.channel = Channel(websocket, expires=60*60, encoding="json")
            status = await ChannelBox.channel_add(self.group_name, self.channel)
            print(" status..", status)

        await websocket.accept()

        print(" add channel..!", self.channel)
        print(" sec-websocket-key..", websocket.headers["sec-websocket-key"])

        groups = await ChannelBox.groups()

        i = len(groups.get(self.group_name))
        print(
            " groups..", f"{groups}"
        )
        print(
            " len..", i
        )


    async def on_disconnect(self, websocket, close_code):

        await ChannelBox.channel_remove(self.group_name, self.channel)
        print("on_disconnect", self.channel)


    async def on_receive(self, websocket, data):
        message = data["message"]
        print(" message..", message)
        name = websocket.user.user_id
        owner_msg = websocket.user.email
        #now_time = datetime.now().strftime(settings.TIME_FORMAT)

        async with async_session() as session:
            # ..
            stmt = await session.execute(
                select(PersonParticipant).where(
                    PersonParticipant.participant == name,
                    PersonParticipant.group_participant == self.group_name,
                )
            )
            odj_true = stmt.scalars().first()
            # ..
            stmt_admin = await session.execute(
                select(MessageChat)
                .join(GroupChat)
                .where(
                    MessageChat.id_group == self.group_name,
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

                await ChannelBox.group_send(self.group_name, payload, history=True)
                # ..
                new = MessageChat()
                new.owner_msg = owner_msg
                new.message = message
                new.id_group = int(self.group_name)
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
        self.channel = None
        self.group_name = None

    async def on_connect(self, websocket):
        self.group_name="MySimpleChat"

        if self.group_name:

            self.channel = Channel(websocket, expires=60*60, encoding="json")
            await ChannelBox.channel_add(self.group_name, self.channel)

            print(" add channel..!", self.channel)
            print(" sec-websocket-key..", websocket.headers["sec-websocket-key"])

            groups = await ChannelBox.groups()

            i = len(groups.get(self.group_name))
            print(
                " groups..", f"{groups}"
            )
            print(
                " len..", i
            )

        await websocket.accept()


    async def on_disconnect(self, websocket, close_code):

        await ChannelBox.channel_remove(self.group_name, self.channel)
        print("on_disconnect", self.channel)


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
                await ChannelBox.group_send(self.group_name, payload, history=True)
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
