from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views.activate_deactivate import ActivateDeactivateView
from users.views.login import LoginView
from users.views.logout import LogoutView
from users.views.password_change import ChangePasswordView, UpdateTheSpecificPassword
from users.views.reset_password import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
)
from users.views.signup import SignupView, UsersViewset
from users.views.telegram_bot import telegram_webhook
from users.views.update_profile import UserProfileViewSet

from .views import ReInvokeSession, SendMessageToTelegram
from .views.send_sms import notify_user

router = DefaultRouter()

router.register(r"users", UsersViewset, basename="users")
urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path("signup", SignupView.as_view(), name="signup"),
    path("forget", PasswordResetRequestView.as_view(), name="forget"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("logout", LogoutView.as_view(), name="logout"),
    path("me", UserProfileViewSet.as_view({"get": "profile"}), name="profile"),
    path(
        "update-profile",
        UserProfileViewSet.as_view({"patch": "update_profile"}),
        name="update-profile",
    ),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path(
        "update-password/", UpdateTheSpecificPassword.as_view(), name="update_password"
    ),
    path("send_sms/", notify_user, name="send_sms"),
    path("telegram", telegram_webhook, name="telegram"),
    path("send-telegram/", SendMessageToTelegram.as_view(), name="send-telegram"),
    path(
        "activate-deactivate/",
        ActivateDeactivateView.as_view(),
        name="activate-deactivate",
    ),
    path("re-invoke-session/", ReInvokeSession.as_view(), name="re-invoke-session"),
]

urlpatterns += router.urls
# path('view', views.MyView.as_view(), name='logout'),
