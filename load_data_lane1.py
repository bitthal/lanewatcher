import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lanewatcher.settings')
django.setup()

from monotainers_stack.models import LaneData

data_lane1 = [
    (8, 'F43E9E', '23040B'),
    (7, '', ''),
    (6, '', ''),
    (5, '', ''),
    (4, '', ''),
    (3, '', ''),
    (2, '', ''),
    (1, '', ''),
]

for position, upper, lower in data_lane1:
    LaneData.objects.create(lane=1, position=position, upper=upper, lower=lower)
