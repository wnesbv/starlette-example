from starlette.routing import Route
from starlette.routing import WebSocketRoute

from .views import (
    ChannelOne,
    ChannelTwo,
    Chat,
    Message,
    Channels,
    ChannelsFlush,
    History,
    HistoryFlush,
)
from .group import group_list, group_details, group_create, group_update, group_delete
from .chat import chat_update, chat_delete


routes = [

    WebSocketRoute("/one_ws", ChannelOne),
    WebSocketRoute("/two_ws", ChannelTwo),
    # ..
    Route("/all", Chat),
    Route("/message", Message),
    Route("/channels", Channels),
    Route("/channels-flush", ChannelsFlush),
    Route("/history", History),
    Route("/history-flush", HistoryFlush),
    # ...
    Route("/update/{id:int}", chat_update, methods=["GET", "POST"]),
    Route("/delete/{id:int}", chat_delete, methods=["GET", "POST"]),
    # ...
    Route("/group/list", group_list),
    Route("/group/{id:int}", group_details),
    # ...
    Route("/group/create/", group_create, methods=["GET", "POST"]),
    Route("/group/update/{id:int}", group_update, methods=["GET", "POST"]),
    Route("/group/delete/{id:int}", group_delete, methods=["GET", "POST"]),

]
