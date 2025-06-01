from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        # if data["new_password"] != data["confirm_new_password"]:
        #     raise serializers.ValidationError(
        #         {"new_password": "New passwords must match."}
        #     )
        validate_password(data["new_password"], self.context["request"].user)
        return data
