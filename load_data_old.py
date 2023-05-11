# import os
# import django
# from time import sleep

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lanewatcher.settings')
# django.setup()

# from monotainers_stack.models import LaneData


# for i in range(100):

#     data = [
#         (8, 'F43E9E'+str(i), '23040B'+str(i), 'F4DE9E'+str(i), str(i)+'23430B'),
#         (7, 'NA', 'NA', str(i)+'F43E6E'+str(i), '22340B'+str(i)),
#         (6, 'NA', 'NA', 'NA', 'NA'),
#         (5, 'NA', 'NA', 'NA', 'NA'),
#         (4, 'NA', 'NA', 'NA', 'NA'),
#         (3, 'NA', 'NA', 'NA', 'NA'),
#         (2, 'NA', 'NA', 'NA', 'NA'),
#         (1, 'NA', 'NA', 'NA', 'NA'),
#     ]

#     # for position, upper1, lower1, upper2, lower2 in data:
#     #     LaneData.objects.create(lane=1, position=position, upper=upper1, lower=lower1)
#     #     LaneData.objects.create(lane=2, position=position, upper=upper2, lower=lower2)
#     # for position, upper1, lower1, upper2, lower2 in data:
#     #     lane1, created1 = LaneData.objects.get_or_create(lane=1, position=position, upper=upper1, lower=lower1)
#     #     lane2, created2 = LaneData.objects.get_or_create(lane=2, position=position, upper=upper2, lower=lower2)
#     for position, upper1, lower1, upper2, lower2 in data:
#         if not upper1:
#             upper1 = None
#         if not lower1:
#             lower1 = None
#         if not upper2:
#             upper2 = None
#         if not lower2:
#             lower2 = None
            
#         lane1, created1 = LaneData.objects.get_or_create(lane=1, position=position, upper=upper1, lower=lower1)
#         lane2, created2 = LaneData.objects.get_or_create(lane=2, position=position, upper=upper2, lower=lower2)

#     sleep(1)


import os
import django
from time import sleep
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pprint

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lanewatcher.settings")
django.setup()

channel_layer = get_channel_layer()

from monotainers_stack.models import LaneData

for i in range(10000):
    data = [
        (8, 'F43E9E'+str(i), '23040B'+str(i), 'F4DE9E'+str(i), '123430B'),
        (7, 'NA', 'NA', 'F43E6E'+str(i), '22340B'+str(i)),
        (6, 'NA', 'NA', 'NA', 'NA'),
        (5, 'NA', 'NA', 'NA', 'NA'),
        (4, 'NA', 'NA', 'NA', 'NA'),
        (3, 'NA', 'NA', 'NA', 'NA'),
        (2, 'NA', 'NA', 'NA', 'NA'),
        (1, 'NA', 'NA', 'NA', 'NA'),
    ]
    
    pprint.pprint(data)

    for row in data:
        position, upper1, upper2, lower1, lower2 = row
        try:
            lane1 = LaneData.objects.get(lane=1, position=position)
            lane1.upper = upper1
            lane1.lower = lower1
            lane1.save()
        except LaneData.DoesNotExist:
            LaneData.objects.create(lane=1, position=position, upper=upper1, lower=lower1)
        try:
            lane2 = LaneData.objects.get(lane=2, position=position)
            lane2.upper = upper2
            lane2.lower = lower2
            lane2.save()
        except LaneData.DoesNotExist:
            LaneData.objects.create(lane=2, position=position, upper=upper2, lower=lower2)

    async_to_sync(channel_layer.group_send)(
        'data_update', 
        {
            'type': 'send_data_update',
        }
    )
    
    print("done for {}".format(i))
    sleep(1)
