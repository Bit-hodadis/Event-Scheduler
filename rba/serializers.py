from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

# from rba.models import CustomGroup


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type"]
        read_only_fields = ["id"]


class GroupSerializer(serializers.ModelSerializer):
    # permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        source="permissions",
        required=False,
    )
    permission_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()  # Add user count field

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            # "permissions",
            "permission_ids",
            "description",
            "permission_count",
            "user_count",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        permissions = validated_data.pop("permissions", [])
        group = super().create(validated_data)
        group.permissions.set(permissions)
        return group

    def update(self, instance, validated_data):
        permissions = validated_data.pop("permissions", None)
        instance = super().update(instance, validated_data)
        if permissions is not None:
            instance.permissions.set(permissions)
        return instance

    def get_permission_count(self, obj):
        # Count the permissions associated with the group
        return obj.permissions.count()

    def get_user_count(self, obj):
        # Use the custom user model to count users in this group

        return obj.users.count()


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ["id", "app_label", "model"]
