from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import ContentTypeSerializer, GroupSerializer, PermissionSerializer

# from rba.models import CustomGroup


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing permissions.
    Only allows read operations (list and retrieve).
    """

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing groups.
    Supports all CRUD operations and custom actions for managing permissions.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        group_name = group.name
        self.perform_destroy(group)
        return Response(
            {"detail": f"Group '{group_name}' deleted successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="add-permission")
    def add_permission(self, request, pk=None):
        """
        Add a permission to the group.
        """
        group = self.get_object()
        permission_id = request.data.get("permission_id")

        if not permission_id:
            return Response(
                {"detail": "Permission ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            permission = Permission.objects.get(id=permission_id)
        except Permission.DoesNotExist:
            return Response(
                {"detail": "Permission not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        group.permissions.add(permission)
        return Response(
            {
                "detail": f"Permission '{permission.name}' added to group '{group.name}'."
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="remove-permission")
    def remove_permission(self, request, pk=None):
        """
        Remove a permission from the group.
        """
        group = self.get_object()
        permission_id = request.data.get("permission_id")

        if not permission_id:
            return Response(
                {"detail": "Permission ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            permission = Permission.objects.get(id=permission_id)
        except Permission.DoesNotExist:
            return Response(
                {"detail": "Permission not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        group.permissions.remove(permission)
        return Response(
            {
                "detail": f"Permission '{permission.name}' removed from group '{group.name}'."
            },
            status=status.HTTP_200_OK,
        )


class UpdatePermissionsView(APIView):
    def post(self, request, role_id):
        role = Group.objects.get(id=role_id)  # Get the role by ID
        permissions = request.data.get("permissions", [])

        # Assuming your permissions are stored as a JSON or as a Many-to-Many relationship
        role.permissions.set(permissions)  # Update the role's permissions
        role.save()

        return Response(
            {"status": "Permissions updated successfully"}, status=status.HTTP_200_OK
        )


class RolePermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing permissions.
    Only allows read operations (list and retrieve).
    """

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Override get_queryset to filter permissions by the user's role.
        If the user has no role, return an empty queryset.
        """
        user = self.request.user

        # Ensure the user has a role attribute and it's not None
        if not hasattr(user, "role") or user.role is None:
            return Permission.objects.none()

        # Filter permissions by the user's role
        return Permission.objects.filter(group=user.role)


class GroupPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        if not request.user.is_authenticated or not request.user.role:
            return False

        if request.user.role.name == "admin":
            return True

        # Get the required permission from the view
        required_permission = view.permission_required

        # Check if any of the user's groups have the required permission
        try:
            group = Group.objects.get(name=request.user.role)
            # user_permissions = request.user.get_user_permissions()
            # print(
            #     user_permissions, " : this is the user permission given to him or her"
            # )
        except Group.DoesNotExist:
            print(f"Group '{request.user}' does not exist.")
            return False
        permissions = group.permissions.all()

        if permissions.filter(codename=required_permission).exists():
            return True

        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        return super().has_object_permission(request, view, obj)


class ContentTypeViewSet(ReadOnlyModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer
