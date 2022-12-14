
from starlette.routing import Route

from .views import item_list, item_details, schedule_rent_list, schedule_service_list


routes = [

    Route("/item-list", item_list),
    Route("/item-details/{id:int}", item_details),
    #..
    Route("/schedule-rent/list", schedule_rent_list),
    Route("/schedule-service/list", schedule_service_list),

]
