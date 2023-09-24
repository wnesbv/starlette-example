from starlette.routing import Route
from starlette.routing import WebSocketRoute

from .views import (
    ChannelOne,
    OneToOneChat,
    ChannelTwo,
)

from .one_one import one_one_details, one_one_update, one_one_delete
from .chat import all_chat, chat_update, chat_delete
from .group import group_list, group_details, group_create, group_update, group_delete



routes = [

    WebSocketRoute("/one_ws/{id:int}", ChannelOne),
    WebSocketRoute("/one_one_ws/{ref_num:str}", OneToOneChat),
    WebSocketRoute("/two_ws", ChannelTwo),

    # ..
    Route("/all", all_chat, methods=["GET", "POST"]),
    #...
    Route("/update/{id_group:int}/{id:int}", chat_update, methods=["GET", "POST"]),
    Route("/delete/{id:int}", chat_delete, methods=["GET", "POST"]),
    #...
    Route("/user/{ref_num:str}", one_one_details),
    Route("/user/update/{ref_num:str}/{id:int}", one_one_update, methods=["GET", "POST"]),
    Route("/user/delete/{id:int}", one_one_delete, methods=["GET", "POST"]),
    #...
    Route("/group/list", group_list),
    Route("/group/{id:int}", group_details),
    #...
    Route("/group/create/", group_create, methods=["GET", "POST"]),
    Route("/group/update/{id:int}", group_update, methods=["GET", "POST"]),
    Route("/group/delete/{id:int}", group_delete, methods=["GET", "POST"]),

]
