# audit/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet, GuestTokenView, LoginLogViewSet

router = DefaultRouter()
router.register(r"audit-logs", AuditLogViewSet, basename="auditlog")
router.register(r"login-logs", LoginLogViewSet, basename="loginlog")
urlpatterns = [
    path("superset", GuestTokenView.as_view(), name="superset"),
]

urlpatterns += router.urls
