from django.contrib.auth.models import AnonymousUser

from utils.current_user import set_current_ip, set_current_user


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not isinstance(request.user, AnonymousUser):

            set_current_user(request.user)
            x_forward = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forward:
                set_current_ip(x_forward.split(",")[0])
            else:
                set_current_ip(request.META.get("REMOTE_ADDR"))
        response = self.get_response(request)
        return response
