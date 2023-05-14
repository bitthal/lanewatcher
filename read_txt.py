import time
import requests
import logging
import os

# Set up logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_filename = os.path.join(log_directory, 'read_text.log')
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

logger = logging.getLogger(__name__)

API_FLUSH_ENDPOINT = "http://46.101.170.185/api/flush_stack_memory/"
API_LOAD_DATA_ENDPOINT = "http://46.101.170.185/table/api/load_data/"


def flush_database():
    try:
        response = requests.post(API_FLUSH_ENDPOINT)
        if response.status_code == 200:
            logger.info("Response: %s", response.json())
        else:
            logger.error("An error occurred: %d %s", response.status_code, response.text)
    except Exception as e:
        logger.exception("An error occurred in flush_database")


def read_file_and_send_data(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            payload = line.split(' ')
            if payload:
                try:
                    response = requests.post(API_LOAD_DATA_ENDPOINT, json=payload)
                    response.raise_for_status()

                    try:
                        data = response.json()['Message']
                        logger.info("%s\n", data)
                    except KeyError as e:
                        logger.exception("KeyError occurred while parsing the response")
                except requests.exceptions.RequestException as e:
                    logger.exception("An error occurred while sending data to the API")
                    break
            break # remove it to run for all lines


if __name__ == "__main__":
    # Flush the database before loading data
    flush_database()

    file_path = "txts/Toronto-112658-112741_AdobeExpress_updated_9th_may.txt"
    read_file_and_send_data(file_path)