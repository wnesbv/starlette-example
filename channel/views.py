
from datetime import datetime
import json
from collections import defaultdict
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

from .img import update_file


templates = Jinja2Templates(directory="templates")


# ..One
class ChannelOne(WebSocketEndpoint):

    is_who = defaultdict(set)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expires = 16000
        self.encoding = "json"
        self.channel = None
        self.group_name = None

    async def on_connect(self, websocket):

        self.group_name = websocket.path_params["id"]
        # print(" group_name..!", self.group_name)
        # print(" websocket dict..", dict(websocket))

        if self.group_name:
            self.channel = Channel(websocket, expires=60*60, encoding="json")
            status = await ChannelBox.channel_add(self.group_name, self.channel)
            print(" status..", status)

        # ..
        await websocket.accept()
        # ..

        print(" add channel..!", self.channel)
        print(" sec-websocket-key..", websocket.headers["sec-websocket-key"])

        # ..
        groups = await ChannelBox.groups()

        is_user = len(groups.get(self.group_name))
        print(
            " groups..", f"{groups}"
        )
        print(
            " len..", is_user
        )

        # ..
        self.is_who[self.group_name].add(str(websocket.user.email))
        print(" add is_who..!", self.is_who)
        payload = {
            "message": is_user,
            "owner": list(self.is_who.get(self.group_name)),
            "created_at": datetime.now().strftime("%H:%M:%S"),
        }
        await ChannelBox.group_send(self.group_name, payload, history=False)


    async def on_disconnect(self, websocket, close_code):

        await ChannelBox.channel_remove(self.group_name, self.channel)
        print(" on_disconnect..", self.channel)
        self.is_who[self.group_name].remove(websocket.user.email)


    async def on_receive(self, websocket, data):

        file = data.get("file")
        message = data.get("message")
        print(" message..", message)
        name = websocket.user.user_id
        owner = websocket.user.email
        #now_time = datetime.now().strftime(settings.TIME_FORMAT)

        async with async_session() as session:
            # ..
            stmt = await session.execute(
                select(PersonParticipant).where(
                    PersonParticipant.owner == name,
                    PersonParticipant.group_participant == self.group_name,
                )
            )
            obj_true = stmt.scalars().first()
            # ..
            stmt_admin = await session.execute(
                select(MessageChat)
                .join(GroupChat)
                .where(
                    MessageChat.id_group == self.group_name,
                    GroupChat.owner == name,
                )
            )
            obj_admin = stmt_admin.scalars().first()
            # ..

            if message:
                if obj_true or obj_admin:
                    payload = {
                        "owner": owner,
                        "message": message,
                    }

                    await ChannelBox.group_send(self.group_name, payload, history=True)
                    # ..
                    new = MessageChat()
                    new.owner = owner
                    new.message = message
                    new.id_group = int(self.group_name)
                    new.created_at = datetime.now()
                    # ..
                    session.add(new)
                    await session.commit()
            if file:
                if obj_true or obj_admin:
                    payload = {
                        "file": file,
                        "owner": owner,
                    }
                    await ChannelBox.group_send(self.group_name, payload, history=True)
                    # ..
                    new = MessageChat()
                    new.file = update_file(self.group_name, file)
                    new.owner = owner
                    new.id_group = int(self.group_name)
                    new.created_at = datetime.now()
                    # ..
                    session.add(new)
                    await session.commit()
        await engine.dispose()


# ..Two
class ChannelTwo(WebSocketEndpoint):

    is_who = defaultdict(set)

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
        # ..
        await websocket.accept()
        # ..
        groups = await ChannelBox.groups()

        is_user = len(groups.get(self.group_name))
        print(
            " groups..", f"{groups}"
        )
        print(
            " len..", is_user
        )

        # ..
        self.is_who[self.group_name].add(str(websocket.user.email))
        print(" add is_who..!", self.is_who)
        payload = {
            "message": is_user,
            "owner": list(self.is_who.get(self.group_name)),
            "created_at": datetime.now().strftime("%H:%M:%S"),
        }
        await ChannelBox.group_send(self.group_name, payload, history=False)


    async def on_disconnect(self, websocket, close_code):

        await ChannelBox.channel_remove(self.group_name, self.channel)
        print("on_disconnect", self.channel)
        self.is_who[self.group_name].remove(websocket.user.email)


    async def on_receive(self, websocket, data):

        file = data.get("file")
        message = data.get("message")
        owner = websocket.user.email
        print(" file..", file)
        print(" message..", message)
        print(" owner..", owner)

        async with async_session() as session:
            if message:
                payload = {
                    "message": message,
                    "owner": owner,
                }
                await ChannelBox.group_send(self.group_name, payload, history=True)
                # ..
                new = OneChat()
                new.message = message
                new.owner = owner
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
            if file:
                payload = {
                    "file": file,
                    "owner": owner,
                }
                await ChannelBox.group_send(self.group_name, payload, history=True)
                # ..
                new = OneChat()
                new.file = update_file(self.group_name, file)
                new.owner = owner
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
