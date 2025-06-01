# audit/views.py
import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from rba.views import GroupPermission
from utils.has_permission import has_custom_permission
from utils.pagination import CustomLimitOffsetPagination

from .models import AuditLog, LoginLog
from .serializers import AuditLogSerializer, LoginLogSerializer


class AuditLogViewSet(ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by("-timestamp")
    serializer_class = AuditLogSerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [GroupPermission]
    permission_required = "view_auditlog"
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ["user__email"]

    def get_queryset(self):
        action = self.request.GET.get("action", None)
        start_date = self.request.GET.get("start_date", None)
        end_date = self.request.GET.get("end_date", None)
        resource = self.request.GET.get("resource", None)

        if start_date:
            self.queryset = self.queryset.filter(created_at__gte=start_date)

        if end_date:
            self.queryset = self.queryset.filter(created_at__lte=end_date)

        if action is not None:
            self.queryset = self.queryset.filter(action=action)
        if resource is not None:
            self.queryset = self.queryset.filter(resource=resource)
        return self.queryset

    def get_permissions(self):
        return has_custom_permission(self, "auditlog")


class LoginLogViewSet(ReadOnlyModelViewSet):
    queryset = LoginLog.objects.all().order_by("-login_time")
    serializer_class = LoginLogSerializer
    permission_classes = [GroupPermission]
    pagination_class = CustomLimitOffsetPagination
    permission_required = "view_loginlog"

    def get_permissions(self):
        return has_custom_permission(self, "loginlog")

    def get_queryset(self):
        session = self.request.COOKIES.get("session")
        queryset = self.queryset.filter(
            user=self.request.user, is_revoked=False
        ).exclude(id=session)
        return queryset


class GuestTokenView(APIView):
    def post(self, request, *args, **kwargs):
        guest_url = "https://reprev.brothersit.dev/api/v1/security/guest_token"
        login_url = "https://reprev.brothersit.dev/api/v1/security/login"

        login_headers = {
            "Content-Type": "application/json",
        }
        dashboard_type = request.data.get("type")

        login_body = {
            "password": "hod1102319",
            "username": "belachew",
            "provider": "db",
            "refresh": True,
        }

        dashboard = {
            "planning": "28067c8c-e8c6-4355-84e7-d359991b9770",
            "preplanning": "5e665f8e-8468-4920-bd40-36de48e043be",
            "performance": "471cd021-adee-4b18-a89d-e1cab83dbc82",
            "collection": "095f5e7b-9eee-443c-b0b8-f4ce084e194b",
        }

        try:
            response = requests.post(login_url, json=login_body, headers=login_headers)
            if response.status_code == 200:
                access_token = response.json().get("access_token")

                if not access_token:
                    return Response(
                        {"error": "Access token not found in response"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                guest_header = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }
                # f5dbb53a-b87d-4514-9784-7beeb81d7c9c
                resource = {
                    "type": "dashboard",
                    "id": dashboard.get(dashboard_type),
                }
                if request.user:
                    role = request.user.role.name if request.user.role else None
                    if role.lower() == "president":
                        resource = {
                            "type": "dashboard",
                            "id": "12c8d9d2-beff-4522-89ec-e6bebdadc02b",
                        }

                guest_body = {
                    "resources": [resource],
                    "rls": [],
                    "user": {
                        "username": "belachew",
                        "first_name": "bel",
                        "last_name": "achew",
                    },
                }

                guest_response = requests.post(
                    guest_url, json=guest_body, headers=guest_header
                )

                if guest_response.status_code == 200:
                    return Response(
                        {"credential": guest_response.json(), "resource": resource},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": guest_response.text},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"error": response.text}, status=status.HTTP_400_BAD_REQUEST
                )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
