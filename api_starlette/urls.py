from starlette.routing import Route

from .views import (
    all_list,
    item_list,
    item_create,
    item_update,
    item_details,
    schedule_rent_list,
    schedule_service_list,
)


routes = [
    Route("/all-list", all_list),
    Route("/item-list", item_list, methods=["GET"]),
    Route("/item-create", item_create, methods=["GET", "POST"],),
    Route("/item-update/{id:int}", item_update, methods=["GET", "POST"],),
    Route("/item-details/{id:int}", item_details),
    # ..
    Route("/schedulerent/list", schedule_rent_list),
    Route("/scheduleservice/list", schedule_service_list),
]
