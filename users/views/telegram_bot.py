# views.py
import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot, Update

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_API")
bot = Bot(token=TELEGRAM_BOT_TOKEN)


@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            update = Update.de_json(data, bot)

            # Process the update
            chat_id = update.message.chat_id
            text = update.message.text

            # Example: Echo the message back
            bot.send_message(chat_id=chat_id, text=f"You said: {text}")

            return JsonResponse({"status": "ok"})
        except Exception as e:
            # Log the error for debugging
            print(f"Error processing update: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse(
        {"status": "error", "message": "Invalid request method"}, status=400
    )
