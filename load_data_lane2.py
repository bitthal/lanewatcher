import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lanewatcher.settings')
django.setup()

from monotainers_stack.models import LaneData

data_lane2 = [
    (8, 'F4DE9E', '23430B'),
    (7, 'F43E6E', '22340B'),
    (6, 'NA', 'NA'),
    (5, 'NA', 'NA'),
    (4, 'NA', 'NA'),
    (3, 'NA', 'NA'),
    (2, 'NA', 'NA'),
    (1, 'NA', 'NA'),
]

for position, upper, lower in data_lane2:
    LaneData.objects.create(lane=2, position=position, upper=upper, lower=lower)
