from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = get_user_model().objects.get(email=email)

        except get_user_model().DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
