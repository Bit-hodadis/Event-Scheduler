# middleware/audit_middleware.py
import logging

logger = logging.getLogger("audit")


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            logger.info(
                {
                    "user": request.user.username,
                    "path": request.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "ip_address": self.get_client_ip(request),
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "query_params": request.GET.dict(),
                }
            )
        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
