
from starlette.routing import Route

from .views import (
    participant_list,
    participant_add,
    participant_create,
    participant_delete,
)


routes = [

    Route("/list/{id:int}", participant_list),
    Route("/{id:int}", participant_add, methods=["GET", "POST"]),
    #...
    Route("/create/{id:int}", participant_create, methods=["GET", "POST"]),
    Route("/delete/{id:int}", participant_delete, methods=["GET", "POST"]),
]
