from datetime import datetime, timedelta

from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from users.serializers.login import LoginSerializer


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(
    ratelimit(key="ip", rate="5/m", method="POST", block=False), name="dispatch"
)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            # Check if the request is rate-limited
            if getattr(request, "limited", False):
                return Response(
                    {
                        "error": "Too many login attempts. Please wait a minute before trying again."
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            # Validate the request data
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            user_id = data.get("id")
            user = CustomUser.objects.get(id=user_id)

            if user.latest_status == "DEACTIVATED":
                return Response(
                    {
                        "error": "This Account is deactivated or blocked please contact the system admin"
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            # print(data, " It is the Data in here also")

            # Set token expiry dates
            expiry_date = datetime.now() + timedelta(days=7)
            expiry_str = expiry_date.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
            expiry_date_access = datetime.now() + timedelta(days=1)
            expiry_str_access = expiry_date_access.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

            # Prepare the response
            response = Response(data, status=status.HTTP_200_OK)

            # Set cookies for tokens
            response.set_cookie(
                key="access_token",
                value=str(data["access"]),
                httponly=True,
                samesite="None",
                secure=True,
                expires=expiry_str_access,
            )
            response.set_cookie(
                key="refresh_token",
                value=str(data["refresh"]),
                httponly=True,
                samesite="None",
                secure=True,
                expires=expiry_str,
            )
            response.set_cookie(
                key="session",
                value=str(data["session"]),
                httponly=True,
                samesite="None",
                secure=True,
                expires=expiry_str,
            )

            # Set CSRF token
            csrf_token = get_token(request)
            response.set_cookie(
                key="csrftoken",
                value=csrf_token,
                httponly=True,
                samesite="None",
                secure=True,
            )

            return response

        except Exception as e:
            print(f"Exception: {str(e)}")  # Debugging
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
