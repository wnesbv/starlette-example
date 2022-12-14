
from starlette.routing import Route

from . import (
    item,
    rent,
    service,
    schedule_rent,
    schedule_service,
    schedule_export_csv,
    schedule_import_csv,

)


routes = [
    Route(
        "/dump_{id:int}",
        schedule_export_csv.export_csv,
        methods=["GET"],
    ),
    #..
    Route(
        "/dump-csv/{id:int}",
        schedule_export_csv.dump_csv,
        methods=["GET"],
    ),
    Route(
        "/dump/{id:int}",
        schedule_export_csv.delete_user_csv,
        methods=["GET", "POST"],
    ),
    #..
    Route(
        "/import-csv/{id:int}",
        schedule_import_csv.import_csv,
        methods=["GET", "POST"],
    ),
    # ..
    Route("/search/", item.search, methods=["GET", "POST"]),
    # ..
    Route("/list", item.item_list),
    Route("/details/{id:int}", item.item_details),

    Route("/create/", item.item_create, methods=["GET", "POST"]),
    Route("/update/{id:int}", item.item_update, methods=["GET", "POST"]),
    Route("/delete/{id:int}", item.item_delete, methods=["GET", "POST"]),
    #
    Route("/file-update/{id:int}", item.item_file_update, methods=["GET", "POST"]),
    Route("/file-delete/{id:int}", item.file_delete, methods=["GET"]),
    # ..
    Route("/rent/list", rent.rent_list),
    Route("/rent/details/{id:int}", rent.rent_details),
    Route("/rent/create/", rent.rent_create, methods=["GET", "POST"]),
    Route("/rent/update/{id:int}", rent.rent_update, methods=["GET", "POST"]),
    Route("/rent/delete/{id:int}", rent.delete, methods=["GET", "POST"]),
    # ..
    Route("/service/list", service.service_list),
    Route("/service/details/{id:int}", service.service_details),
    Route("/service/create/", service.service_create, methods=["GET", "POST"]),
    Route("/service/update/{id:int}", service.service_update, methods=["GET", "POST"]),
    Route("/service/delete/{id:int}", service.delete, methods=["GET", "POST"]),
    #
    Route("/service/file-update/{id:int}", service.file_update, methods=["GET", "POST"]),
    Route("/service/file-delete/{id:int}", service.file_delete, methods=["GET"]),
    # ..
    Route("/schedule-rent/list", schedule_rent.list_rent),
    Route(
        "/schedule-rent/details/{id:int}",
        schedule_rent.details_rent,
        methods=["GET", "POST"],
    ),
    Route("/schedule-rent/create/", schedule_rent.create_rent, methods=["GET", "POST"]),
    Route(
        "/schedule-rent/update/{id:int}",
        schedule_rent.update_rent,
        methods=["GET", "POST"],
    ),
    Route(
        "/schedule-rent/delete/{id:int}", schedule_rent.delete, methods=["GET", "POST"]
    ),
    # ..
    Route("/schedule-service/list_id_service", schedule_service.list_service_id),
    Route("/schedule-service/list/{id:int}", schedule_service.list_service),
    Route(
        "/schedule-service/details/{service:int}/{id:int}",
        schedule_service.details_service,
        methods=["GET", "POST"],
    ),
    Route(
        "/schedule-service/create/",
        schedule_service.create_service,
        methods=["GET", "POST"],
    ),
    Route(
        "/schedule-service/update/{id:int}",
        schedule_service.update_service,
        methods=["GET", "POST"],
    ),
    Route(
        "/schedule-service/delete/{id:int}",
        schedule_service.delete,
        methods=["GET", "POST"],
    ),
]
