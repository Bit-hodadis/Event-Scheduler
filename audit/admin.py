# audit/admin.py
from django.contrib import admin

from .models import AuditLog, LoginLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "resource", "timestamp", "ip_address")
    search_fields = ("user__username", "resource", "action")


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "login_time", "ip_address")
    search_fields = ("user__username", "ip_address")
