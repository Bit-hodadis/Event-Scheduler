from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import LoginLog


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response = Response({"message": "Logout successful."})
        session = request.COOKIES.get("session")
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        response.delete_cookie("session")

        try:
            login_log = LoginLog.objects.filter(id=session).first()
            login_log.delete()
        except Exception as e:
            print(e)

        response.delete_cookie("csrftoken")
        return response
