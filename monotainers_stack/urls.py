from django.urls import path
from . import views, api


urlpatterns = [
    path('table/', views.table, name='table'),  # Update the view function name here
    path('fetch_data/', views.fetch_data, name='fetch_data'),
    path('get_lane_data/', views.get_lane_data, name='get_lane_data'),
    path('api/load_data/', api.load_data_call, name='load_data_call'),
    path('flush_stack_memory/', api.flush_stack_memory, name='flush_stack_memory'),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

