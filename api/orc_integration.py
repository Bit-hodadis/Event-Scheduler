import os

import requests


def fetch_data_orc_api():
    url = os.getenv("ORC_API_URL")  # Replace with the actual API endpoint
    headers = {
        "Authorization": f"Bearer {os.getenv("ORC_API_KEY")}"
    }  # Include your API key if needed

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Assuming the response is in JSON format
        data = response.json()
        name = data.name
        amount = data.amount
        checkin_time = data.checkin_time

        return data
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None
