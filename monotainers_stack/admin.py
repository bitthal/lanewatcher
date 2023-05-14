from django.contrib import admin

# Register your models here.
from .models import Planogram, Pending, Processed, LaneData

admin.site.register(Planogram)
admin.site.register(Pending)
admin.site.register(Processed)
admin.site.register(LaneData)

