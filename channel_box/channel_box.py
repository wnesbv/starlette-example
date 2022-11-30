
import time
import uuid
from starlette.endpoints import WebSocketEndpoint


class ChannelBox:
    def __init__(self):
        self.created = time.time()

    _CHANNELS = {}
    created = None


    async def channel_send(
        self, channel_name, payload
    ):
        for channel in self._CHANNELS.get(channel_name, {}):
            await channel.send(payload)


    async def channels_flush(self):

        self._CHANNELS = {}


    async def _channel_add(self, channel_name, channel):

        self._CHANNELS.setdefault(channel_name, {})
        self._CHANNELS[channel_name][channel] = True


    async def _remove_channel(self, channel_name, channel):

        if channel in self._CHANNELS.get(channel_name, {}):
            del self._CHANNELS[channel_name][channel]

        if not any(self._CHANNELS.get(channel_name, {})):
            try:
                del self._CHANNELS[channel_name]
            except:
                pass

        await self._clean_expired()


    async def _clean_expired(self):

        for channel_name in list(self._CHANNELS):

            for channel in self._CHANNELS.get(channel_name, {}):
                is_expired = await channel.is_expired()
                if is_expired:
                    del self._CHANNELS[channel_name][channel]

            if not any(self._CHANNELS.get(channel_name, {})):
                try:
                    del self._CHANNELS[channel_name]
                except:
                    pass


channel_box = ChannelBox()


class Channel:

    def __init__(self, websocket, expires, encoding):
        self.channel_uuid = str(uuid.uuid1())
        self.websocket = websocket
        self.expires = expires
        self.encoding = encoding
        self.created = time.time()


    async def send(self, payload):

        websocket = self.websocket
        if self.encoding == "json":
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                pass
        elif self.encoding == "text":
            try:
                await websocket.send_text(payload)
            except RuntimeError:
                pass
        elif self.encoding == "bytes":
            try:
                await websocket.send_bytes(payload)
            except RuntimeError:
                pass
        else:
            try:
                await websocket.send(payload)
            except RuntimeError:
                pass
        self.created = time.time()


    async def is_expired(self):
        return self.expires + int(self.created) < time.time()

    def __repr__(self):
        return f"Channel uuid={self.channel_uuid} expires={self.expires} encoding={self.encoding}"


class ChannelBoxEndpoint(WebSocketEndpoint):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.expires = 60 * 60 * 24
        self.encoding = "json"
        self.channel_name = None
        self.channel = None
        self.channel_box = channel_box


    async def on_connect(self, websocket, **kwargs):

        await super().on_connect(websocket, **kwargs)
        self.channel = Channel(
            websocket=websocket, expires=self.expires, encoding=self.encoding
        )


    async def on_disconnect(self, websocket, close_code):

        await super().on_disconnect(websocket, close_code)
        await self.channel_box._remove_channel(self.channel_name, self.channel)


    async def channel_send(self, payload):

        await self.channel_box.channel_send(
            self.channel_name, payload
        )


    async def channel_get_or_create(
        self,
        channel_name,
        websocket=None
    ):
        if websocket:
            self.channel = Channel(
                websocket=websocket, expires=self.expires, encoding=self.encoding
            )
        await self.channel_box._channel_add(channel_name, self.channel)

        self.channel_name = channel_name
