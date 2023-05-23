from monotainers_stack.models import LaneData, Pending, Planogram, Processed
import os
import django
from time import sleep
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pprint
import sqlite3
from . import db_setup, db2_setup
import logging, os, json
import re
from collections import defaultdict
from .db2_setup import return_empty_positions
from pprint import pformat
import textwrap
import datetime

import shutil

def reset_files():
    pending_file = 'txts/pending.txt'
    processed_file = 'txts/processed.txt'
    pending_default_file = 'txts/pending_default.txt'

    # Delete pending.txt and processed.txt if they exist
    if os.path.exists(pending_file):
        os.remove(pending_file)

    if os.path.exists(processed_file):
        os.remove(processed_file)

    # Create a fresh pending.txt by copying content from pending_default.txt
    shutil.copyfile(pending_default_file, pending_file)
reset_files()

TEMP_FILE_NAME = 'txts/device_count_temp_file.json'
def delete_temp_file():
    if os.path.exists(TEMP_FILE_NAME):
        os.remove(TEMP_FILE_NAME)
delete_temp_file()


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


# def append_matrix_to_file(planogram, pending, realtime, processed, file_name):
#     temp_realtime = []
#     for i in realtime:
#         for j in i:
#             temp_realtime.append(j)
#     lists = [planogram, pending, temp_realtime, processed]
#     max_length = max(len(lst) for lst in lists)
#     max_rows = max_length // 6 + (1 if max_length % 6 else 0)  # calculate rows for each list-matrix

#     # Append the list-matrices to the file
#     with open(file_name, 'a') as f:
#         for row in range(max_rows):
#             for lst in lists:
#                 for col in range(6):  # fixed width of 8
#                     index = row * 6 + col
#                     # If the current list has this index, write the value
#                     if index < len(lst):
#                         cell_value = str(lst[index])
#                     # If not, write a blank space
#                     else:
#                         cell_value = ''
#                     # Write the value with fixed width of 10
#                     f.write(f'{cell_value:<10}')
#                 # Write some space between list-matrices
#                 f.write('\t')
#             # Write a newline character at the end of each row
#             f.write('\n')
#         # Write a separator line after each set of rows
#         f.write('-' * (6 * 11 * len(lists)) + '\n')


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
    planogram_values, pending_values, realtime_values, processed_values = calculate_and_update_values(
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
    
    # Convert tuple to list and replace None with ''
    db_data = [[item if item is not None else '' for item in list(row)] for row in db_data]

    realtime_values = db_data
    logger.info(realtime_values)

    # Build the data list using the fetched rows
    data = [
        (row[0], row[2], row[3], row[4], row[5])
        for row in db_data
    ]

    conn.close()

    # append_matrix_to_file(planogram_values, pending_values, realtime_values, processed_values, 'output.txt')
    save_data_to_db(data, lane_number)
    logger.info("Data processing complete")
    return "success"


# def process_data2(payload):
#     # logger.info("Processing data payload")
#     db2_setup.setup_database()

#     values = [payload[0]] + payload[-4:]
#     frame_id, device_id, lane_name, lane_section, position = values
#     position = int(position.strip())
#     logger.info(str(f'REAL TIME: [{frame_id}, {device_id}, {lane_name}, {lane_section}, {position}]'))
#     logger.info("=========================================================")
#     # Determine the lane number based on the lane name
#     lane_number = 1 if lane_name == "Hamilton" else 2
#     # logger.debug(f"Determined lane_number {lane_number} based on lane_name {lane_name}")

#     conn = sqlite3.connect("stack_memory2.db")
#     cursor = conn.cursor()

#     # Calculate and update values
#     planogram_values, pending_values, realtime_values, processed_values = calculate_and_update_values(
#         frame_id, device_id, lane_name, lane_section, position)

#     # Serialize the data
#     planogram_data = json.dumps(planogram_values)
#     pending_data = json.dumps(pending_values)
#     processed_data = json.dumps(processed_values)
#     realtime_data = json.dumps(realtime_values)

#     # Check if a row with the given lane_number exists
#     cursor.execute("SELECT COUNT(*) FROM lane_data WHERE lane_number = ?", (lane_number,))
#     exists = cursor.fetchone()[0]

#     if exists:
#         # Update lane_data
#         cursor.execute("""
#             UPDATE lane_data SET lane_name = ?, planogram_data = ?, pending_data = ?, realtime_data = ?, processed_data = ?
#             WHERE lane_number = ?
#         """, (lane_name, planogram_data, pending_data, realtime_data, processed_data, lane_number))
#     else:
#         # Insert a new row with the given lane_number and calculated values
#         cursor.execute("""
#             INSERT INTO lane_data (lane_number, lane_name, planogram_data, pending_data, realtime_data, processed_data)
#             VALUES (?, ?, ?, ?, ?, ?)
#         """, (lane_number, lane_name, planogram_data, pending_data, realtime_data, processed_data))

#     conn.commit()
#     logger.critical(str(f"Calculated: {planogram_data}, {pending_data}, {realtime_data}, {processed_data}"))
#     logger.info("Database updated successfully")

#     # append_matrix_to_file(planogram_values, pending_values, realtime_values, processed_values, 'output.txt')
#     # logger.info("Data processing complete")
#     return "success"



# Call the function at the beginning of your program


def get_pending_data():
    try:
        # Read data from the file
        with open('txts/pending.txt', 'r') as file:
            data = file.read()

        if not data.strip():
            return {}

        devices_by_city = defaultdict(list)
        lines = data.strip().split('\n')

        for line in lines:
            tokens = line.split(' ')
            lane_name = tokens[2]
            device_id = tokens[1]

            # Check if device_id is 6 characters long and alphanumeric
            if len(device_id) == 6 and re.match(r'^[A-Za-z0-9]+$', device_id):
                devices_by_city[lane_name].append(device_id)

        return dict(devices_by_city)
    except Exception as e:
        return dict({"Error": e})


def get_processed_data():
    try:
        # Read data from the file
        with open('txts/processed.txt', 'r') as file:
            data = file.read()

        if not data.strip():
            return {}

        devices_by_city = defaultdict(list)
        lines = data.strip().split('\n')

        for line in lines:
            tokens = line.split(' ')
            lane_name = tokens[2]
            device_id = tokens[1]

            # Check if device_id is 6 characters long and alphanumeric
            if len(device_id) == 6 and re.match(r'^[A-Za-z0-9]+$', device_id):
                devices_by_city[lane_name].append(device_id)

        return dict(devices_by_city)
    except Exception as e:
        return dict({"Error": e})


def pending_to_processed(device_id, city_name):
    pending_file = 'txts/pending.txt'
    processed_file = 'txts/processed.txt'
    updated_lines = []
    found = False

    # Read the contents of the pending file
    with open(pending_file, 'r') as file:
        lines = file.readlines()

    # Check each line and keep the ones without the specified device_id and city_name
    for line in lines:
        line_tokens = line.strip().split(' ')
        if device_id not in line or line_tokens[-1] != city_name:
            updated_lines.append(line)
        else:
            found = True

    if not found:
        print(f"Device ID {device_id} with city {city_name} not found in the pending file.")
        return

    # Write the updated contents back to the pending file
    with open(pending_file, 'w') as file:
        file.writelines(updated_lines)

    # Append a new line with the timestamp, device_id, and city_name to the processed file
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(processed_file, 'a') as file:
        file.write(f"\n{timestamp} {device_id} {city_name}")

    
    
def device_id_genuine(device_id):
    pending_file = 'txts/pending.txt'
    processed_file = 'txts/processed.txt'

    # Check the pending file for the device_id
    with open(pending_file, 'r') as file:
        pending_data = file.read()
        if device_id in pending_data:
            return True

    # Check the processed file for the device_id
    with open(processed_file, 'r') as file:
        processed_data = file.read()
        if device_id in processed_data:
            return True

    # If the device_id is not found in either file, return False
    return False
    
def device_id_exists(device_id, real_time_positions):
    for i in range(len(real_time_positions)):
        if real_time_positions[i]['upper']['monotainer_id'] == device_id:
            past_position = i+1
            past_lane = 'upper'
            break
        elif real_time_positions[i]['lower']['monotainer_id'] == device_id:
            past_position = i+1
            past_lane = 'lower'
            break
        else:
            past_position = False
            past_lane = False
    return past_position, past_lane

# def calculate_and_update_values(frame_id, device_id, lane_name, lane_section, position):
#     # logger.info(f"Calculating and updating values for frame_id {frame_id}, device_id {device_id}, lane_name {lane_name}, lane_section {lane_section}, position {position}")
#     # try:
#     # Determine the lane number based on the lane name
#     lane_number = 1 if lane_name == "Hamilton" else 2

#     # logger.info("Getting all stack data")
#     conn = sqlite3.connect("stack_memory2.db")
#     cursor = conn.cursor()
#     lane_data_rows = cursor.execute("SELECT * FROM lane_data WHERE lane_number=?", (lane_number,)).fetchall()
#     logger.critical(str(f'MEMORY DB : {lane_data_rows}'))

#     # Calculate the required values (dummy values for now)
#     pending_dict = get_pending_data()
#     planogram_values = [10, 5, 3, 18, 2, 1]
#     pending_values = pending_dict[lane_name]
#     processed_values = ['L7M8N1', 'L7M8N2', 'L7M8N3', 'L7M8N4', 'L7M8N5', 'L7M8N6']
    
#     return planogram_values, pending_values, [1, 2, 3, 4, 5], processed_values
    

def calculate_and_update_values(frame_id, device_id, lane_name, lane_section, position):
    updated_value = False
    processed_list = []
    past_position = 0
    past_lane = 0
    # Determine the lane number based on the lane name
    lane_number = 1 if lane_name == "Hamilton" else 2

    # Open connection
    conn = sqlite3.connect("stack_memory2.db")
    cursor = conn.cursor()

    # Fetch data
    lane_data_rows = cursor.execute("SELECT * FROM lane_data WHERE lane_number=?", (lane_number,)).fetchall()
    try:
        in_stage_count = 0
        dd = lane_data_rows[0] # because single tuple is inside a list
        rt_positions = dd[5]
        rt_list = json.loads(rt_positions)
        realtime_list = []
        for item in rt_list:
            if len(item['upper']['monotainer_id'])>3:
                in_stage_count += 1
            if len(item['lower']['monotainer_id'])>3:
                in_stage_count += 1
            # realtime_list.append(item['upper']['monotainer_id'])
        #     # ttt.join(item['lower'], ' ')
            
        logging.info(f"\n{pformat(in_stage_count)}\n")
    except Exception as e:
        realtime_list = []
        logger.error(f'{lane_number} - {e}')
        logging.info(f"\nerrorrrrrr: {pformat(lane_data_rows)}\n")
    
    
    try:
        pending_dict = get_pending_data()
        try:
            pending_values = pending_dict[lane_name]
        except:
            pending_values = []
    
        # defining planogram to update existing values in database
        pending_data = {
            "monotainers": [{"monotainer_id": mid} for mid in pending_values],
            "total_monotainers": len(pending_values)
        }
    except:
        pending_values = []
        pending_data = {
            "monotainers": {},
            "total_monotainers": 0
        }
        logger.error(pending_dict)
    
    
    # Getting Real time positions from memory
    # Find the row with the specified lane_number
    lane_data_row = None
    for row in lane_data_rows:
        if row[1] == lane_number:  # Assuming lane_number is at index 1 in the row
            lane_data_row = row
            break

    if lane_data_row:
        # Get the index of the realtime_data column in the row (replace 'column_index' with the actual index)
        column_index = 5
        # Load the realtime_data JSON string into a Python list
        real_time_positions = json.loads(lane_data_row[column_index])
        
        copy_real_time = []
        i = 0
        for element in real_time_positions:
            if element['position'] == int(position):
                if device_id_genuine(device_id):
                    # past_position, past_lane = device_id_exists(device_id, real_time_positions)
                    if int(position)<=7:
                        if len(real_time_positions[8-(int(position)+1)]['lower']['monotainer_id'])>3 and len(real_time_positions[8-(int(position)+1)]['upper']['monotainer_id'])>3:
                            element[lane_section.lower()]['monotainer_id'] = device_id
                            updated_value = True
                    else:
                        element[lane_section.lower()]['monotainer_id'] = device_id
                        updated_value = True
                    
                # real_time_positions[i][lane_section.lower()]['monotainer_id'] = device_id
            copy_real_time.append(element)
            i += 1
        
        # final_copy_real_time = []
        # if past_position and past_lane:
        #     for element in copy_real_time:
        #         if element['position'] == int(position):
        #             if int(position) == 1 and past_lane == 'lower':
        #                 pass
        #             else:
        #                 element[past_lane]['monotainer_id'] = 'NA'
        #         final_copy_real_time.append(element)
                    
        
        logger.info(f"{frame_id}, {lane_name}, {lane_section}, {position}, {device_id}, {copy_real_time}")
    else:
        real_time_positions = return_empty_positions()

    # real_time_positions = [
    #     {
    #         "position": pos,
    #         "upper": {"monotainer_id": "NA", "misplaced": 0},
    #         "lower": {"monotainer_id": "NA", "misplaced": 0}
    #     } for pos in range(8, 0, -1)
    # ]

    
    
    # Read values from processed txt file
    try:
        processed_dict = get_processed_data()
        try:
            processed_values = processed_dict[lane_name]
        except:
            processed_values = []
        
        # defining planogram to update existing values in database
        processed_data = {
            "monotainers": [{"monotainer_id": mid} for mid in processed_values],
            "total_monotainers": len(processed_values),
        }
    except:
        processed_values = []
        processed_data = {
            "monotainers": {},
            "total_monotainers": 0
        }
        logger.error(f"\n\n\n Error - {processed_dict}")        


    # first fetch these values from db and then Calculate the values
    mapped = len(processed_values)
    total = 21
    missing = total - mapped
    trucks_required = 0
    trucks_ordered = 0
    
    # defining planogram to update existing values in database
    planogram_data = {
        "in_stage": in_stage_count,
        "mapped": mapped,
        "missing": missing,
        "total": total,
        "trucks_required": trucks_required,
        "trucks_ordered": trucks_ordered
    }


    # # Construct data dictionary
    # data = {
    #     "lane_number": lane_number,
    #     "lane_name": lane_name,
    #     "planogram_data": json.dumps(planogram_data),
    #     "pending_data": json.dumps(pending_data),
    #     "realtime_data": json.dumps(real_time_positions),
    #     "processed_data": json.dumps(processed_data)
    # }


    # just to show properly in log file
    # max_width = 50

    # formatted_pending_values = "\n".join(textwrap.wrap(pformat(pending_values), max_width))
    # formatted_realtime_list = "\n".join(textwrap.wrap(pformat(realtime_list), max_width))
    # formatted_processed_list = "\n".join(textwrap.wrap(pformat(processed_values), max_width))

    # lines_pending = formatted_pending_values.splitlines()
    # lines_realtime = formatted_realtime_list.splitlines()
    # lines_processed = formatted_processed_list.splitlines()

    # max_lines = max(len(lines_pending), len(lines_realtime), len(lines_processed))

    # output_lines = []

    # for i in range(max_lines):
    #     line_pending = lines_pending[i] if i < len(lines_pending) else " " * max_width
    #     line_realtime = lines_realtime[i] if i < len(lines_realtime) else " " * max_width
    #     line_processed = lines_processed[i] if i < len(lines_processed) else " " * max_width

    #     output_line = f"{line_pending:<{max_width}} {line_realtime:<{max_width}} {line_processed:<{max_width}}"
    #     output_lines.append(output_line)

    # output = "\n".join(output_lines)
    # logger.info("Pending Values                                |                    Realtime List                    |              Processed List\n%s", output)
    if updated_value:
        pending_to_processed(device_id, lane_name)
    return planogram_data, pending_data, real_time_positions, processed_data




def process_data2(payload):
    db2_setup.setup_database()
    # Load the device count dictionary from the temporary file
    if os.path.exists(TEMP_FILE_NAME):
        with open(TEMP_FILE_NAME, 'r') as temp_file:
            device_count = json.load(temp_file)
    else:
        device_count = {}

    values = [payload[0]] + payload[-4:]
    frame_id, device_id, lane_name, lane_section, position = values

    # Create a unique key for the combination of device_id, lane_name, lane_section, and position
    key = (device_id, lane_name, lane_section, position)

    # Convert the key to a string, as JSON does not support tuples as keys
    key_str = json.dumps(key)

    # Increase the count of occurrences for the key
    device_count[key_str] = device_count.get(key_str, 0) + 1

    # If the count of occurrences exceeds 5, store the value in the database
    if (int(position) == 6 or int(position) == 3):
        count_limit = 2
    else:
        if (int(position) == 3 and lane_section == 'Upper'):
            count_limit = 8
        else:
            count_limit = 6
        
    if device_count[key_str] >= count_limit:
        # Calculate and update values
        planogram_values, pending_values, realtime_values, processed_values = calculate_and_update_values(
            frame_id, device_id, lane_name, lane_section, position)

        # Serialize the data
        planogram_data = json.dumps(planogram_values)
        pending_data = json.dumps(pending_values)
        processed_data = json.dumps(processed_values)
        realtime_data = json.dumps(realtime_values)

        store_in_database(lane_name, planogram_data, pending_data, realtime_data, processed_data)
        # Reset the count for the key to prevent duplicate entries
        device_count[key_str] = 0

    # Save the updated device count dictionary to the temporary file
    with open(TEMP_FILE_NAME, 'w') as temp_file:
        json.dump(device_count, temp_file)



def store_in_database(lane_name, planogram_data, pending_data, realtime_data, processed_data):
    conn = sqlite3.connect('stack_memory2.db')
    cursor = conn.cursor()

    # Determine the lane number based on the lane name
    lane_number = 1 if lane_name == "Hamilton" else 2

    # Check if a row with the given lane_number exists
    cursor.execute("SELECT COUNT(*) FROM lane_data WHERE lane_number = ?", (lane_number,))
    exists = cursor.fetchone()[0]
    
    if exists:
        # Update lane_data
        cursor.execute("""
            UPDATE lane_data SET lane_name = ?, planogram_data = ?, pending_data = ?, realtime_data = ?, processed_data = ?
            WHERE lane_number = ?
        """, (lane_name, planogram_data, pending_data, realtime_data, processed_data, lane_number))
        # logger.info(f"Pushed in database: {realtime_data}")
    else:
        # Insert a new row with the given lane_number and calculated values
        cursor.execute("""
            INSERT INTO lane_data (lane_number, lane_name, planogram_data, pending_data, realtime_data, processed_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (lane_number, lane_name, planogram_data, pending_data, realtime_data, processed_data))

    conn.commit()
    conn.close()