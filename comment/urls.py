
from starlette.routing import Route

from . import views

routes = [

    Route(
        "/item/create/{id:int}",
        views.cmt_item_create,
        methods=["GET", "POST"]
    ),
    Route(
        "/rent/create/{id:int}",
        views.cmt_rent_create,
        methods=["GET", "POST"]
    ),
    Route(
        "/service/create/{id:int}",
        views.cmt_service_create,
        methods=["GET", "POST"]
    ),
    #..
    Route(
        "/item/update/{id:int}",
        views.cmt_item_update,
        methods=["GET", "POST"]
    ),
    Route(
        "/rent/update/{id:int}",
        views.cmt_rent_update,
        methods=["GET", "POST"]
    ),
    Route(
        "/service/update/{id:int}",
        views.cmt_service_update,
        methods=["GET", "POST"]
    ),
    #..
    Route(
        "/delete/{id:int}",
        views.cmt_delete,
        methods=["GET", "POST"]
    ),
]
