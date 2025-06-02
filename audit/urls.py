# audit/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet, LoginLogViewSet

router = DefaultRouter()
router.register(r"audit-logs", AuditLogViewSet, basename="auditlog")
router.register(r"login-logs", LoginLogViewSet, basename="loginlog")
urlpatterns = []

urlpatterns += router.urls
