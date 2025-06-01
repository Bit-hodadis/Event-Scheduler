from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ContentTypeViewSet,
    GroupViewSet,
    PermissionViewSet,
    RolePermissionViewSet,
    UpdatePermissionsView,
)

router = DefaultRouter()
router.register(r"content-types", ContentTypeViewSet, basename="contenttype")
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"groups", GroupViewSet, basename="group")
router.register(r"has-permission", RolePermissionViewSet, basename="has_permission")
urlpatterns = [
    path("", include(router.urls)),
    path(
        "groups/<int:role_id>/update_permissions/",
        UpdatePermissionsView.as_view(),
        name="update_permissions",
    ),
]
