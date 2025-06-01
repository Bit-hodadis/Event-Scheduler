# views.py
import os

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.send_telegram import send_to_telegram


class SendMessageToTelegram(APIView):
    def post(self, request):
        """
        Sends a message to a Telegram group or channel.
        Expected JSON payload:
        {
            "bot_token": "your_bot_token",
            "chat_id": "your_chat_id",
            "text": "Your message here",
            "parse_mode": "HTML"  # Optional
        }
        """
        # Extract data from the request
        bot_token = os.getenv("TELEGRAM_BOT_API")
        chat_id = request.data.get("chat_id")
        text = request.data.get("text")
        parse_mode = request.data.get("parse_mode", None)  # Optional

        # Validate required fields
        if not bot_token or not chat_id or not text:
            return Response(
                {"error": "Missing required fields: bot_token, chat_id, or text"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Send the message to Telegram
            response = send_to_telegram(bot_token, chat_id, text, parse_mode)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to send message: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
