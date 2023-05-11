import os
import django
from time import sleep
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pprint
import sqlite3
from . import db_setup


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lanewatcher.settings")
django.setup()

channel_layer = get_channel_layer()

from monotainers_stack.models import LaneData

def save_data_to_db(processed_payload):
    # for i in range(100):
    # data = [
    #     (8, 'F43E9E'+str(i), '23040B'+str(i), 'F4DE9E'+str(i), '123430B'),
    #     (7, 'NA', 'NA', 'F43E6E'+str(i), '22340B'+str(i)),
    #     (6, 'NA', 'NA', 'NA', 'NA'),
    #     (5, 'NA', 'NA', 'NA', 'NA'),
    #     (4, 'NA', 'NA', 'NA', 'NA'),
    #     (3, 'NA', 'NA', 'NA', 'NA'),
    #     (2, 'NA', 'NA', 'NA', 'NA'),
    #     (1, 'NA', 'NA', 'NA', 'NA'),
    # ]
    # pprint.pprint(processed_payload)
    for row in processed_payload:
        position, upper1, lower1, upper2, lower2 = row
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


# def process_data(payload):
#     db_setup.setup_database()

#     values = [payload[0]] + payload[-4:]
#     num_values = len(values)
#     print(num_values)
#     end_result_data = values

#     frame_id, device_id, lane_name, lane_section, position = values
#     position = int(position.strip())

#     conn = sqlite3.connect("stack_memory.db")
#     cursor = conn.cursor()

#     if lane_name == "Hamilton":
#         if lane_section == "Upper":
#             cursor.execute("UPDATE stack_memory SET upper_lane1 = ? WHERE position = ?", (device_id, position))
#         elif lane_section == "Lower":
#             cursor.execute("UPDATE stack_memory SET lower_lane1 = ? WHERE position = ?", (device_id, position))
#     elif lane_name == "Toronto":
#         if lane_section == "Upper":
#             cursor.execute("UPDATE stack_memory SET upper_lane2 = ? WHERE position = ?", (device_id, position))
#         elif lane_section == "Lower":
#             cursor.execute("UPDATE stack_memory SET lower_lane2 = ? WHERE position = ?", (device_id, position))

#     conn.commit()
#     conn.close()
    
#     data = [
#         (8, 'F43E9E'+str(i), '23040B'+str(i), 'F4DE9E'+str(i), '123430B'),
#         (7, 'NA', 'NA', 'F43E6E'+str(i), '22340B'+str(i)),
#         (6, 'NA', 'NA', 'NA', 'NA'),
#         (5, 'NA', 'NA', 'NA', 'NA'),
#         (4, 'NA', 'NA', 'NA', 'NA'),
#         (3, 'NA', 'NA', 'NA', 'NA'),
#         (2, 'NA', 'NA', 'NA', 'NA'),
#         (1, 'NA', 'NA', 'NA', 'NA'),
#     ]

#     return values, end_result_data


def process_data(payload):
    db_setup.setup_database()

    values = [payload[0]] + payload[-4:]
    num_values = len(values)
    print(num_values)
    end_result_data = values

    frame_id, device_id, lane_name, lane_section, position = values
    position = int(position.strip())

    conn = sqlite3.connect("stack_memory.db")
    cursor = conn.cursor()

    if lane_name == "Hamilton":
        if lane_section == "Upper":
            cursor.execute("UPDATE stack_memory SET upper_lane1 = ? WHERE position = ?", (device_id, position))
        elif lane_section == "Lower":
            cursor.execute("UPDATE stack_memory SET lower_lane1 = ? WHERE position = ?", (device_id, position))
    elif lane_name == "Toronto":
        if lane_section == "Upper":
            cursor.execute("UPDATE stack_memory SET upper_lane2 = ? WHERE position = ?", (device_id, position))
        elif lane_section == "Lower":
            cursor.execute("UPDATE stack_memory SET lower_lane2 = ? WHERE position = ?", (device_id, position))

    conn.commit()

    # Fetch the data from the database
    cursor.execute("SELECT * FROM stack_memory ORDER BY position DESC")
    db_data = cursor.fetchall()

    # Build the data list using the fetched rows
    data = [
        (row[0], row[1], row[2], row[3], row[4])
        for row in db_data
    ]

    conn.close()
    
    save_data_to_db(data)

    return data, num_values