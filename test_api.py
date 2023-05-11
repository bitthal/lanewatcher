import requests

API_ENDPOINT = "http://64.226.75.48/table/api/load_data/"

def test_api():
    test_payload = [
        (8, 'F43E9ET', '23040BT', 'F4DE9ET', '123430BT'),
        (7, 'NA', 'NA', 'F43E6ET', '22340BT'),
        (6, 'NA', 'NA', 'NA', 'NA'),
        (5, 'NA', 'NA', 'NA', 'NA'),
        (4, 'NA', 'NA', 'NA', 'NA'),
        (3, 'NA', 'NA', 'NA', 'NA'),
        (2, 'NA', 'NA', 'NA', 'NA'),
        (1, 'NA', 'NA', 'NA', 'NA'),
    ]

    response = requests.post(API_ENDPOINT, json=test_payload)

    if response.status_code == 200:
        print("API is running fine.")
        print("Response:", response.json())
    else:
        print("API returned an error. Status code:", response.status_code)
        print("Response:", response.text)
        
def test_flush():

    url = "http://46.101.170.185/api/flush_stack_memory/"

    response = requests.post(url)

    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("An error occurred:", response.status_code, response.text)


if __name__ == "__main__":
    # test_api()
    test_flush()

