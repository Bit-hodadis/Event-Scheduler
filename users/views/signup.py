from django.db import transaction

# from utils.send_email import send_verification_email
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from exceptions import EmailSendError
from rba.views import GroupPermission
from users.models import CustomUser
from users.serializers.user import UserSerializer
from utils.has_permission import has_custom_permission
from utils.pagination import CustomLimitOffsetPagination


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    # send_verification_email(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except EmailSendError:
                return Response(
                    {
                        "detail": "User registration failed. Verification email could not be sent."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewset(ModelViewSet):
    pagination_class = CustomLimitOffsetPagination
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ["first_name", "last_name", "username", "email", "role__name"]
    permission_classes = [GroupPermission]
    permission_required = "view_customuser"

    def get_queryset(self):
        # Get the address from query parameters
        address = self.request.query_params.get("address", None)
        role = self.request.query_params.get("role", None)

        # If no address is provided, return an empty queryset
        if not address:
            return CustomUser.objects.none()
        if role is not None and role != "":
            return CustomUser.objects.filter(address=address, role=role)

        # Filter the queryset based on the address
        return CustomUser.objects.filter(address=address)

    def get_permissions(self):
        return has_custom_permission(self, "customuser")
