from monotainers_stack.models import LaneData, Pending, Planogram, Processed
import os
import django
from time import sleep
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pprint
import sqlite3
from . import db_setup
import logging, os

# Set up logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_filename = os.path.join(log_directory, 'load_data.log')
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lanewatcher.settings")
django.setup()

channel_layer = get_channel_layer()


def save_data_to_db(processed_payload, lane_number):
    try:
        logger.info(f"Saving data to the database for lane_number {lane_number}")
        # Extracting the calculated values
        planogram_values, pending_values, processed_values = calculate_and_update_values('frame_id', 'device_id', 'lane_name', 'lane_section', position)

        # Saving data for LaneData
        for row in processed_payload:
            position, upper1, lower1, upper2, lower2 = row
            try:
                lane = LaneData.objects.get(lane=lane_number, position=position)
                lane.upper = upper1
                lane.lower = lower1
                lane.save()
            except LaneData.DoesNotExist:
                LaneData.objects.create(
                    lane=lane_number, position=position, upper=upper1, lower=lower1)

        # Saving data for Planogram
        try:
            planogram = Planogram.objects.get(lane_number=lane_number)
            planogram.in_staged, planogram.mapped, planogram.missing, planogram.total, planogram.trucks_required, planogram.trucks_ordered = planogram_values
            planogram.save()
        except Planogram.DoesNotExist:
            Planogram.objects.create(lane_number=lane_number, in_staged=planogram_values[0], mapped=planogram_values[1], missing=planogram_values[
                                    2], total=planogram_values[3], trucks_required=planogram_values[4], trucks_ordered=planogram_values[5])

        # Saving data for Pending
        for pending_id in pending_values:
            Pending.objects.get_or_create(lane=planogram, pending_id=pending_id)

        # Saving data for Processed
        for processed_id in processed_values:
            Processed.objects.get_or_create(
                lane=planogram, processed_id=processed_id)

        async_to_sync(channel_layer.group_send)(
            'data_update',
            {
                'type': 'send_data_update',
            }
        )
    except Exception as e:
        logger.exception(f"An error occurred while saving data to the database for lane_number {lane_number}")


def append_matrix_to_file(planogram, pending, realtime, processed, file_name):
    lists = [planogram, pending, realtime, processed]
    logger.info(str(lists))
    print(lists)
    # max_length = max(len(lst) for lst in lists)
    # max_rows = max_length // 8 + (1 if max_length % 8 else 0)  # calculate rows for each list-matrix

    # # Append the list-matrices to the file
    # with open(file_name, 'a') as f:
    #     for row in range(max_rows):
    #         for lst in lists:
    #             for col in range(8):  # fixed width of 8
    #                 index = row * 8 + col
    #                 # If the current list has this index, write the value
    #                 if index < len(lst):
    #                     f.write(str(lst[index]) + '\t')
    #                 # If not, write a blank space
    #                 else:
    #                     f.write('\t')
    #             # Write some space between list-matrices
    #             f.write('\t\t')
    #         # Write a newline character at the end of each row
    #         f.write('\n')
    #     # Write a separator line after each set of rows
    #     f.write('-' * (8 * 8 * len(lists)) + '\n')


def calculate_and_update_values(frame_id, device_id, lane_name, lane_section, position):
    logger.info(f"Calculating and updating values for frame_id {frame_id}, device_id {device_id}, lane_name {lane_name}, lane_section {lane_section}, position {position}")
    # TODO: Replace these dummy values with your own logic
    planogram_values = [10, 5, 3, 18, 2, 1]
    pending_values = ['L7M8N7', 'L7M8N8', 'L7M8N9']
    processed_values = ['L7M8N1', 'L7M8N2',
                        'L7M8N3', 'L7M8N4', 'L7M8N5', 'L7M8N6']

    return planogram_values, pending_values, processed_values


def process_data(payload):
    logger.info("Processing data payload")
    db_setup.setup_database()

    values = [payload[0]] + payload[-4:]
    frame_id, device_id, lane_name, lane_section, position = values
    position = int(position.strip())

    # Determine the lane number based on the lane name
    lane_number = 1 if lane_name == "Hamilton" else 2
    logger.debug(f"Determined lane_number {lane_number} based on lane_name {lane_name}")

    conn = sqlite3.connect("stack_memory.db")
    cursor = conn.cursor()

    # Update real_time_positions
    if lane_section == "Upper":
        cursor.execute(
            "UPDATE real_time_positions SET upper_lane1 = ? WHERE position = ? AND lane_number = ?",
            (device_id, position, lane_number)
        )
    elif lane_section == "Lower":
        cursor.execute(
            "UPDATE real_time_positions SET lower_lane1 = ? WHERE position = ? AND lane_number = ?",
            (device_id, position, lane_number)
        )

    # Calculate and update values
    planogram_values, pending_values, processed_values = calculate_and_update_values(
        frame_id, device_id, lane_name, lane_section, position)

    # Update planogram
    cursor.execute("""
        INSERT INTO planogram (lane_number, lane_name, in_staged, mapped, missing, total, trucks_required, trucks_ordered)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (lane_number, lane_name, *planogram_values))

    # Update pending
    for pending_id in pending_values:
        cursor.execute("""
            INSERT INTO pending (lane_number, pending_id)
            VALUES (?, ?)
        """, (lane_number, pending_id))

    # Update processed
    for processed_id in processed_values:
        cursor.execute("""
            INSERT INTO processed (lane_number, processed_id)
            VALUES (?, ?)
        """, (lane_number, processed_id))

    conn.commit()
    logger.info("Database updated successfully")

    # Fetch the data from the database
    cursor.execute(
        "SELECT * FROM real_time_positions WHERE lane_number = ? ORDER BY position DESC", (lane_number,))
    db_data = cursor.fetchall()
    realtime_values = db_data

    # Build the data list using the fetched rows
    data = [
        (row[0], row[2], row[3], row[4], row[5])
        for row in db_data
    ]

    conn.close()

    append_matrix_to_file(planogram_values, pending_values, realtime_values, processed_values, 'output.txt')
    save_data_to_db(data, lane_number)
    logger.info("Data processing complete")
    return "success"
