from datetime import datetime

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from user_agents import parse as parse_user_agent

# from utils.current_user import get_current_ip
from audit.models import LoginLog


class LoginSerializer(TokenObtainPairSerializer):
    username_field = "email"
    remember_me = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        remember_me = attrs.get("remember_me", False)

        if not email or not password:
            raise ValidationError(
                {
                    "detail": "Both email and password are required.",
                    "code": "missing_credentials",
                }
            )

        # Authenticate user using email
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not user:
            raise AuthenticationFailed(
                detail="Invalid email or password.", code="authorization"
            )

        if not user.is_active:
            raise AuthenticationFailed(
                detail="This account is inactive.", code="inactive_account"
            )

        # Generate token using parent method
        data = super().validate(attrs)
        request = self.context.get("request")
        ip = None
        x_forward = request.META.get("HTTP_X_FORWARDED_FOR")

        user_agent_str = request.META.get("HTTP_USER_AGENT", "")
        user_agent = parse_user_agent(user_agent_str)

        print(remember_me, "it is remember ME")

        device_type = (
            "Mobile"
            if user_agent.is_mobile
            else (
                "Tablet"
                if user_agent.is_tablet
                else "PC" if user_agent.is_pc else "Other"
            )
        )
        os = user_agent.os.family  # e.g., 'iOS', 'Windows'
        browser = user_agent.browser.family  # e.g., 'Chrome', 'Safari'

        if x_forward:

            ip = x_forward.split(",")[0]

        else:
            ip = request.META.get("REMOTE_ADDR")
        login_log = LoginLog.objects.create(
            user=user,
            ip_address=ip,
            login_time=timezone.now(),
            device_name=device_type,
            os=os,
            is_remember=remember_me,
            browser=browser,
            user_agent=user_agent_str,
        )
        # data.save()
        # Add additional user data
        if user.role:
            data.update(
                {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "address": user.address.id if user.address else None,
                    "address_name": user.address.name if user.address else None,
                    "id": user.id,
                    "role": user.role.name,
                    "session": login_log.id,
                }
            )
        else:
            data.update(
                {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "id": user.id,
                    "address": user.address.id if user.address else None,
                    "address_name": user.address.name if user.address else None,
                    "role": None,
                    "session": login_log.id,
                }
            )

        return data
