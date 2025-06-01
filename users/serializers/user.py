from rest_framework import serializers

from users.models import CustomUser, UserHasStatus


class LatestUserStatusSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()

    class Meta:
        model = UserHasStatus
        fields = ["status", "reason", "changed_by", "timestamp"]

    def get_changed_by(self, obj):
        return obj.changed_by.email


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    password = serializers.CharField(write_only=True)
    latest_status = serializers.SerializerMethodField()
    latest_status_history = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = "__all__"

    def create(self, validated_data):
        # Pop the password and hash it
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user

    def get_latest_status(self, obj):
        return obj.latest_status

    def get_latest_status_history(self, obj):
        latest_status = obj.status_history.order_by("-timestamp").first()
        return (
            LatestUserStatusSerializer(latest_status).data
            if latest_status
            else {"status": "ACTIVE"}
        )
