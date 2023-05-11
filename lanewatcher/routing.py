# # lanewatcher/routing.py

# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import path
# from monotainers_stack import consumers

# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#         "websocket": URLRouter(
#             [
#                 path("ws/data_update/", consumers.DataUpdateConsumer.as_asgi()),
#             ]
#         ),
#     }
# )



# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import re_path
# from django.core.asgi import get_asgi_application
# from monotainers_stack import consumers

# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#         "websocket": URLRouter(
#             [
#                 re_path(r"ws/data_update/$", consumers.DataUpdateConsumer.as_asgi()),
#             ]
#         ),
#     }
# )


# from channels.routing import ProtocolTypeRouter
# from django.urls import re_path
# from django.core.asgi import get_asgi_application

# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#     }
# )


from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from monotainers_stack import consumers

websocket_urlpatterns = [
    path('ws/data_update', consumers.MyConsumer.as_asgi()), # Replace MyConsumer with the name of your consumer class
]

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    }
)
