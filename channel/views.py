from datetime import datetime

import json

from collections import defaultdict

from sqlalchemy.future import select

from starlette.templating import Jinja2Templates
from starlette.endpoints import WebSocketEndpoint

from channel_box import Channel, ChannelBox

from db_config.storage_config import engine, async_session

from channel.models import MessageGroup, OneChat, OneOneChat

from auth_privileged.opt_slc import get_privileged_user

from .img import update_file
from .opt_slc import (
    prv_true,
    user_true,
    prv_admin_true,
    user_admin_true,
    prv_owner,
    user_owner,
    prv_community,
    user_community,
    group_ref_num,
)


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

        if (
            self.group_name
            and websocket["user"].is_authenticated
            or websocket["prv"].is_authenticated
        ):
            self.channel = Channel(websocket, expires=60 * 60, encoding="json")
            status = await ChannelBox.channel_add(self.group_name, self.channel)
            print(" status..", status)
            # ..
            await websocket.accept()
            # ..
            print(" add channel..!", self.channel)
            print(" sec-websocket-key..", websocket.headers["sec-websocket-key"])
            # ..
            groups = await ChannelBox.groups()
            # ..
            is_user = len(groups.get(self.group_name))
            print(" groups..", f"{groups}")
            print(" len..", is_user)
            # ..
            if websocket["user"].is_authenticated:
                self.is_who[self.group_name].add(str(websocket.user.email))
            if websocket["prv"].is_authenticated:
                self.is_who[self.group_name].add(str(websocket["prv"].prv_key))
            # ..
            print(" add is_who..!", self.is_who)
            # ..
            payload = {
                "message": is_user,
                "owner": list(self.is_who.get(self.group_name)),
                "created_at": datetime.now().strftime("%H:%M:%S"),
            }
            await ChannelBox.group_send(self.group_name, payload, history=False)

    async def on_disconnect(self, websocket, close_code):
        await ChannelBox.channel_remove(self.group_name, self.channel)
        print(" on_disconnect..", self.channel)
        if websocket["user"].is_authenticated:
            self.is_who[self.group_name].remove(websocket.user.email)
        if websocket["prv"].is_authenticated:
            self.is_who[self.group_name].remove(websocket["prv"].prv_key)

    async def on_receive(self, websocket, data):
        # ..
        file = data.get("file")
        message = data.get("message")
        # ..
        print(" message..", message)
        # ..
        if websocket["user"].is_authenticated:
            name = websocket.user.user_id
            owner = websocket.user.email
            print(" name..", name)
        if websocket["prv"].is_authenticated:
            owner = websocket["prv"].prv_key

        # now_time = datetime.now().strftime(settings.TIME_FORMAT)

        async with async_session() as session:
            # ..
            if websocket["prv"].is_authenticated:
                # ..
                obj_true = await prv_true(self, websocket, session)
                obj_admin = await prv_admin_true(self, websocket, session)
            # ..
            if websocket["user"].is_authenticated:
                # ..
                obj_true = await user_true(self, websocket, session)
                obj_admin = await user_admin_true(self, websocket, session)
            # ...
            if message:
                if obj_true or obj_admin:
                    payload = {
                        "owner": owner,
                        "message": message,
                    }

                    await ChannelBox.group_send(self.group_name, payload, history=True)
                    # ..
                    new = MessageGroup()
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
                    new = MessageGroup()
                    new.file = update_file(self.group_name, file)
                    new.owner = owner
                    new.id_group = int(self.group_name)
                    new.created_at = datetime.now()
                    # ..
                    session.add(new)
                    await session.commit()
        await engine.dispose()


# ..One to One
class OneToOneChat(WebSocketEndpoint):
    is_who = defaultdict(set)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expires = 16000
        self.encoding = "json"
        self.channel = None
        self.group_name = None

    async def on_connect(self, websocket):
        # ..
        self.group_name = websocket.path_params["ref_num"]
        # ..
        if websocket["user"].is_authenticated:
            self.is_who[self.group_name].add(str(websocket.user.email))
        if websocket["prv"].is_authenticated:
            self.is_who[self.group_name].add(str(websocket["prv"].prv_key))
        # ..
        if self.group_name:
            self.channel = Channel(websocket, expires=60 * 60, encoding="json")
            status = await ChannelBox.channel_add(self.group_name, self.channel)
            print(" status..", status)
            print(" group_name..", self.group_name)
            # print(" websocket..", dict(websocket))
            # ..
            await websocket.accept()
            # ..
            print(" add channel..!", self.channel)
            print(" sec-websocket-key..", websocket.headers["sec-websocket-key"])
            # ..
            groups = await ChannelBox.groups()
            # ..
            is_user = len(groups.get(self.group_name))
            print(" groups..", f"{groups}")
            print(" len..", is_user)
            # ..
            if websocket["user"].is_authenticated:
                self.is_who[self.group_name].add(str(websocket.user.email))
            if websocket["prv"].is_authenticated:
                self.is_who[self.group_name].add(str(websocket["prv"].prv_key))
            # ..
            print(" add is_who..!", self.is_who)
            # ..
            payload = {
                "message": is_user,
                "owner": list(self.is_who.get(self.group_name)),
                "created_at": datetime.now().strftime("%H:%M:%S"),
            }
            await ChannelBox.group_send(self.group_name, payload, history=False)

    async def on_disconnect(self, websocket, close_code):
        await ChannelBox.channel_remove(self.group_name, self.channel)
        print(" on_disconnect..", self.channel)
        if websocket["user"].is_authenticated:
            self.is_who[self.group_name].remove(websocket.user.email)
        if websocket["prv"].is_authenticated:
            self.is_who[self.group_name].remove(websocket["prv"].prv_key)

    async def on_receive(self, websocket, data):
        # ..
        file = data.get("file")
        message = data.get("message")
        # ..
        print(" message..", message)
        # ..
        if websocket["user"].is_authenticated:
            name = websocket.user.user_id
            owner = websocket.user.email
            print(" name..", name)
        if websocket["prv"].is_authenticated:
            owner = websocket["prv"].prv_key

        async with async_session() as session:
            # ..
            one_one = await group_ref_num(self, session)
            # ..
            if websocket["prv"].is_authenticated:
                # ..
                obj_owner = await prv_owner(self, websocket, session)
                obj_community = await prv_community(self, websocket, session)
            # ..
            if websocket["user"].is_authenticated:
                # ..
                obj_owner = await user_owner(self, websocket, session)
                obj_community = await user_community(self, websocket, session)
            # ...
            if message:
                if obj_owner or obj_community:
                    payload = {
                        "owner": owner,
                        "message": message,
                    }
                    print(" payload..", payload)
                    # ..
                    await ChannelBox.group_send(self.group_name, payload, history=True)
                    # ..
                    new = OneOneChat()
                    new.owner = owner
                    new.message = message
                    new.one_one = one_one.id
                    new.created_at = datetime.now()
                    # ..
                    session.add(new)
                    await session.commit()
            if file:
                if obj_true:
                    payload = {
                        "file": file,
                        "owner": owner,
                    }
                    await ChannelBox.group_send(self.group_name, payload, history=True)
                    # ..
                    new = OneOneChat()
                    new.file = update_file(self.group_name, file)
                    new.owner = owner
                    new.one_one = one_one.id
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
        self.group_name = "all chat"
        # ..
        if (
            self.group_name
            and websocket["user"].is_authenticated
            or websocket["prv"].is_authenticated
        ):
            self.channel = Channel(websocket, expires=60 * 60, encoding="json")
            await ChannelBox.channel_add(self.group_name, self.channel)

            print(" add channel..!", self.channel)
            print(" sec-key..", websocket.headers["sec-websocket-key"])
            print(" websocket..!", dict(websocket))
            print(" prv..!", websocket["prv"])
            # ..
            await websocket.accept()
            # ..
            groups = await ChannelBox.groups()
            # ..
            is_user = len(groups.get(self.group_name))
            # ..
            print(" groups..", f"{groups}")
            print(" len..", is_user)
            # ..
            if websocket["user"].is_authenticated:
                self.is_who[self.group_name].add(str(websocket.user.email))
            if websocket["prv"].is_authenticated:
                self.is_who[self.group_name].add(str(websocket["prv"].prv_key))
            # ..
            print(" add is_who..!", self.is_who)
            # ..
            payload = {
                "message": is_user,
                "owner": list(self.is_who.get(self.group_name)),
                "created_at": datetime.now().strftime("%H:%M:%S"),
            }
            await ChannelBox.group_send(self.group_name, payload, history=False)

    async def on_disconnect(self, websocket, close_code):
        await ChannelBox.channel_remove(self.group_name, self.channel)
        print("on_disconnect", self.channel)

        if websocket["user"].is_authenticated:
            self.is_who[self.group_name].remove(websocket.user.email)
        if websocket["prv"].is_authenticated:
            self.is_who[self.group_name].remove(websocket["prv"].prv_key)

    async def on_receive(self, websocket, data):
        # ..
        file = data.get("file")
        message = data.get("message")
        # ..
        async with async_session() as session:
            prv = await get_privileged_user(websocket, session)
            if message:
                if websocket["user"].is_authenticated:
                    owner = websocket.user.email
                if websocket["prv"].is_authenticated:
                    owner = prv.email
                # ..
                print(" file..", file)
                print(" message..", message)
                print(" owner..", owner)
                # ..
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
