from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser, UserHasStatus


class ActivateDeactivateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user_id = request.data["user_id"]
            message = request.data["reason"]
            user = CustomUser.objects.get(id=user_id)
            if user.latest_status == "ACTIVE":
                if message:
                    UserHasStatus.objects.create(
                        status="DEACTIVATED",
                        changed_by=request.user,
                        user=user,
                        reason=message,
                    )
                    return Response(
                        {"message": "Deactivated successfully"},
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    UserHasStatus.objects.create(
                        status="DEACTIVATED", changed_by=request.user, user=user
                    )
                    return Response(
                        {"message": "Deactivated successfully"},
                        status=status.HTTP_201_CREATED,
                    )
            else:
                UserHasStatus.objects.create(
                    status="ACTIVE", changed_by=request.user, user=user
                )
                return Response(
                    {"message": "Activated successfully"},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
