
from starlette.routing import Mount

from admin.urls import routes as admin_routes
from item.urls import routes as item_routes
from account.urls import routes as account_routes
from comment.urls import routes as comment_routes
from channel.urls import routes as channel_routes
from participant.urls import routes as participant_routes
from make_an_appointment.urls import routes as reserve_routes

# ..
from api_starlette.urls import routes as api_routes


routes = [
    Mount("/admin", routes=admin_routes),
    # ..
    Mount("/item", routes=item_routes),
    Mount("/account", routes=account_routes),
    Mount("/comment", routes=comment_routes),
    Mount("/chat", routes=channel_routes),
    Mount("/participant", routes=participant_routes),
    Mount("/reserve", routes=reserve_routes),
    # ..
    Mount("/api", routes=api_routes),

]
