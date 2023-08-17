
from starlette.routing import Route

from . import user, item, rent, slider, service, schedule_rent, schedule_service, comment


routes = [
    Route("/", item.all_list),
    # ..
    Route("/user/list", user.i_list),
    Route("/user/details/{id:int}", user.i_details),
    Route("/user/create/", user.i_create, methods=["GET", "POST"]),
    Route("/user/update/{id:int}", user.i_update, methods=["GET", "POST"]),
    Route("/user/update-password/{id:int}", user.i_update_password, methods=["GET", "POST"]),
    Route("/user/delete/{id:int}", user.i_delete, methods=["GET", "POST"]),
    # ..
    Route("/item/list", item.item_list),
    Route("/item/details/{id:int}", item.item_details),
    Route("/item/create/", item.item_create, methods=["GET", "POST"]),
    Route("/item/update/{id:int}", item.item_update, methods=["GET", "POST"]),
    Route("/item/delete/{id:int}", item.item_delete, methods=["GET", "POST"]),
    # ...
    Route("/rent/list", rent.item_list),
    Route("/rent/details/{id:int}", rent.item_details),
    Route("/rent/create/", rent.item_create, methods=["GET", "POST"]),
    Route("/rent/update/{id:int}", rent.item_update, methods=["GET", "POST"]),
    Route("/rent/delete/{id:int}", rent.item_delete, methods=["GET", "POST"]),
    # ...
    Route("/service/list", service.item_list),
    Route("/service/details/{id:int}", service.item_details),
    Route("/service/create/", service.item_create, methods=["GET", "POST"]),
    Route("/service/update/{id:int}", service.item_update, methods=["GET", "POST"]),
    Route("/service/delete/{id:int}", service.item_delete, methods=["GET", "POST"]),
    # ..
    Route(
        "/delete-rent-csv",
        schedule_rent.delete_rent_csv,
        methods=["GET"],
    ),
    Route(
        "/delete-service-csv",
        schedule_service.delete_service_csv,
        methods=["GET"],
    ),


    # ..schedule rent
    Route("/schedule-rent/list", schedule_rent.rent_list),
    Route(
        "/schedule-rent/details/{id:int}",
        schedule_rent.rent_details,
        methods=["GET", "POST"],
    ),
    Route("/schedule-rent/create/", schedule_rent.item_create, methods=["GET", "POST"]),
    Route(
        "/schedule-rent/update/{id:int}",
        schedule_rent.item_update,
        methods=["GET", "POST"],
    ),
    Route(
        "/schedule-rent/delete/{id:int}",
        schedule_rent.item_delete,
        methods=["GET", "POST"],
    ),

    # ..schedule service
    Route("/schedule-service/list/", schedule_service.sch_list),
    Route("/schedule-service/user-sch/{id:int}", schedule_service.user_list),
    Route("/schedule-service/srv-sch/{id:int}", schedule_service.srv_list),

    Route("/schedule-service/all-user-sch-list", schedule_service.all_user_sch_list),

    Route(
        "/schedule-service/details/{user:int}/{service:int}",
        schedule_service.sch_details,
        methods=["GET", "POST"],
    ),
    Route(
        "/schedule-service/create/",
        schedule_service.item_create,
        methods=["GET", "POST"],
    ),
    Route(
        "/schedule-service/update/{id:int}",
        schedule_service.item_update,
        methods=["GET", "POST"],
    ),
    Route(
        "/schedule-service/delete/{id:int}",
        schedule_service.item_delete,
        methods=["GET", "POST"],
    ),
    # ..
    Route(
        "/comment/item/create/{id:int}",
        comment.cmt_item_create,
        methods=["GET", "POST"],
    ),
    Route(
        "/comment/service/create/{id:int}",
        comment.cmt_service_create,
        methods=["GET", "POST"],
    ),
    Route(
        "/comment/rent/create/{id:int}",
        comment.cmt_rent_create,
        methods=["GET", "POST"],
    ),
    # ..
    Route(
        "/comment/item/update/{id:int}",
        comment.cmt_item_update,
        methods=["GET", "POST"],
    ),
    Route(
        "/comment/service/update/{id:int}",
        comment.cmt_service_update,
        methods=["GET", "POST"],
    ),
    Route(
        "/comment/rent/update/{id:int}",
        comment.cmt_rent_update,
        methods=["GET", "POST"],
    ),
    # ..
    Route("/comment/delete/{id:int}", comment.cmt_delete, methods=["GET", "POST"]),
    # ...
    Route("/slider/list", slider.slider_list),
    Route("/slider/details/{id:int}", slider.slider_details),
    Route("/slider/create/", slider.slider_create, methods=["GET", "POST"]),
    Route("/slider/update/{id:int}", slider.slider_update, methods=["GET", "POST"]),
    Route("/slider/delete/{id:int}", slider.slider_delete, methods=["GET", "POST"]),
    Route("/slider/file-update/{id:int}", slider.slider_file_update, methods=["GET", "POST"]),
    Route("/slider/file-delete/{id:int}", slider.slider_file_delete, methods=["GET"]),
]
