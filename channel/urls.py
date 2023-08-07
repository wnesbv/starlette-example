from starlette.routing import Route
from starlette.routing import WebSocketRoute

from .views import (
    ChannelOne,
    ChannelTwo,
    all_chat,
    Message,
    Groups,
    GroupsFlush,
    History,
    HistoryFlush,
)
from .group import group_list, group_details, group_create, group_update, group_delete
from .chat import chat_update, chat_delete


routes = [

    WebSocketRoute("/one_ws/{id:int}", ChannelOne),
    WebSocketRoute("/two_ws", ChannelTwo),
    # ..
    Route("/all", all_chat, methods=["GET", "POST"]),
    Route("/text", Message),
    Route("/channels", Groups),
    Route("/channels-flush", GroupsFlush),
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
