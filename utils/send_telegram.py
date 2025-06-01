# utils/send_telegram.py
import requests


def send_to_telegram(bot_token, chat_id, text, parse_mode=None):
    """
    Sends a message to a Telegram group or channel.
    :param bot_token: Your Telegram bot token.
    :param chat_id: The chat ID of the group or channel.
    :param text: The message text to send.
    :param parse_mode: Optional. Supports 'HTML' or 'MarkdownV2' for formatting.
    :return: Response from the Telegram API.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    response = requests.post(url, json=payload)
    return response.json()
