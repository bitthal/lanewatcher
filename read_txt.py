import time
import requests

API_FLUSH_ENDPOINT = "http://64.226.75.48/api/flush_stack_memory/"
API_LOAD_DATA_ENDPOINT = "http://64.226.75.48/table/api/load_data/"

def flush_database():
    response = requests.post(API_FLUSH_ENDPOINT)

    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("An error occurred:", response.status_code, response.text)

def read_file_and_send_data(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            payload = line.split(' ')
            if payload:
                try:
                    response = requests.post(API_LOAD_DATA_ENDPOINT, json=payload)
                    response.raise_for_status()
                    data = (response.json()['Success'])
                    for line in data:
                        print(line)
                    print('-'*200)
                except requests.exceptions.RequestException as e:
                    print("An error occurred while sending data to the API:", str(e))
                    break
                
                # time.sleep(0.3)

if __name__ == "__main__":
    # Flush the database before loading data
    flush_database()

    file_path = "txts/Toronto-112658-112741_AdobeExpress_full_.txt"
    read_file_and_send_data(file_path)
