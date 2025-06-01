import os

import requests


def send_sms(to, message, is_bulk=False):
    """
    Sends an SMS using the Afro Message API.

    Parameters:
    - to (str): The recipient's phone number in international format (e.g., '+251911234567').
    - message (str): The content of the SMS.

    Returns:
    - dict: The response from the Afro Message API.
    """
    api_url = os.getenv("AFRO_MESSAGE_API_URL")
    api_key = os.getenv("AFRO_MESSAGE_API_KEY")
    if is_bulk:
        api_url += "/bulk_send"
    else:
        api_url += "/send"

    if not api_url or not api_key:
        raise ValueError(
            "AFRO_MESSAGE_API_URL or AFRO_MESSAGE_API_KEY is not set in the environment variables."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "to": "251965917665",
        "message": "message",
    }

    response = requests.post(api_url, json=payload, headers=headers)

    print("response", response.json())

    return response
