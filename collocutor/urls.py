
from starlette.routing import Route

from .views import (
    call_owner,
    call_to_user,
    collocutor_add,
    collocutor_create,
    collocutor_delete,
)


routes = [

    Route("/owner-list", call_owner),
    Route("/to-user-list", call_to_user),
    Route("/add/{id:int}", collocutor_add, methods=["GET", "POST"]),
    #...
    Route("/create", collocutor_create, methods=["GET", "POST"]),
    Route("/delete/{id:int}", collocutor_delete, methods=["GET", "POST"]),
]
