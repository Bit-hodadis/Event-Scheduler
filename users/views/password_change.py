from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from users.serializers.password_change import PasswordChangeSerializer


class ChangePasswordView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            # update_session_auth_hash(
            #     request, user
            # )  # Important to keep the user logged in after password change
            return Response(
                {"detail": "Password has been changed successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateTheSpecificPassword(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        # Validate required fields
        if not data.get("id") or not data.get("password"):
            return Response(
                {"detail": "Missing required fields: id and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Attempt to retrieve user by ID
            user = CustomUser.objects.get(id=data["id"])
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Update user password
        user.set_password(data["password"])
        user.save()

        return Response(
            {"detail": "Password updated successfully"}, status=status.HTTP_200_OK
        )
