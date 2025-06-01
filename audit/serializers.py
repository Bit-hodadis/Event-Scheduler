# audit/serializers.py
from rest_framework import serializers

from .models import AuditLog, LoginLog


class UserSerializer(serializers.Serializer):
    email = serializers.CharField()
    # class Meta:
    #     fields = "__all__"
    #     model = CustomUser


class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = "__all__"


class LoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginLog
        fields = "__all__"
