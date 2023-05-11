# """
# ASGI config for lanewatcher project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lanewatcher.settings')

# application = get_asgi_application()


# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import re_path
# from monotainers_stack import consumers

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lanewatcher.settings')

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


# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import re_path
# from monotainers_stack import consumers

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lanewatcher.settings')

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

# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import re_path
# from monotainers_stack import consumers

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lanewatcher.settings')

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

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from django.urls import path
from monotainers_stack import consumers  # Replace `myapp` with the name of the app containing your WebSocket consumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lanewatcher.settings')

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/data_update/", consumers.DataUpdateConsumer.as_asgi()),
                ]
            )
        ),
    }
)


