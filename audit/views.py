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
