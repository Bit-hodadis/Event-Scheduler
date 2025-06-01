from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import LoginLog


class ReInvokeSession(APIView):
    def post(self, request):
        session = request.data.get("session")
        login_log = LoginLog.objects.filter(id=session).first()
        if login_log:
            login_log.is_revoked = True
            login_log.save()
        response = Response({"message": "Session re-invoked."})
        return response
