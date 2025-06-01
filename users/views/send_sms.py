from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from utils.send_sms import send_sms


@api_view(["POST"])
def notify_user(request):
    user_phone_number = [
        {"to": "251947333232", "message": "MSG_1"},
        {"to": "251995183367", "message": "MSG_2"},
    ]
    # , "+251995183367")
    # Replace with the actual user's phone number
    message = "Hello, ጠ   this is a test message from our Django application."
    result = send_sms("+251965917665", message, is_bulk=False)
    print(result.json(), " it is json")
    if result.json().get("acknowledge") == "success":
        return Response({"message": "successfully"}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": "faild to send"}, status=status.HTTP_400_BAD_REQUEST
        )


# IQ8wpbuKvRaQXks30dQ0Blp1lUqvB8HnueV92FN1c016c4f2
