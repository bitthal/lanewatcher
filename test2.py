import re
from collections import defaultdict

def get_device_ids_by_city():
    try:
        # Read data from the file
        with open('txts/pending.txt', 'r') as file:
            data = file.read()
            
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


print(get_device_ids_by_city())