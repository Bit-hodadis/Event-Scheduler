from datetime import datetime, timedelta, timezone

import jwt
import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import resolve
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from audit.models import LoginLog

User = get_user_model()


# def get_user_from_token(token):
#     try:
#         # Decode the token
#         access_token = AccessToken(token)
#         # Extract the user ID from the token payload
#         user_id = access_token["user_id"]
#         print(user_id, "user ID is HERE")
#         # Retrieve the user from the database
#         user = User.objects.get(id=user_id)
#         return user
#     except User.DoesNotExist:
#         return None
#     except Exception as e:
#         print(e)
#         return None


class AttachJWTTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url_name = resolve(path=request.path).url_name
        if url_name == "login" or url_name == "signup":
            pass
        else:
            token = request.COOKIES.get("access_token")

            if token:
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        response = self.get_response(request)
        return response


class AutoRefreshTokenMiddleware:
    """
    Middleware to automatically refresh the access token when it's expired
    and a valid refresh token is present.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    # def check_user_status(self, user):
    #     if user is not None:
    #         if user.latest_status is not None:
    #             if user.latest_status.status == "inactive":

    #                 return JsonResponse(
    #                     {"error": "Your Account is  InActive please Contact the Admin"},
    #                     status=status.HTTP_401_UNAUTHORIZED,
    #                 )
    #     return None

    def decode_access_token(self, access_token):
        """
        Decodes the access token and retrieves the payload.
        """
        try:
            payload = jwt.decode(
                access_token,
                settings.SIMPLE_JWT["SIGNING_KEY"],
                algorithms=[api_settings.ALGORITHM],
            )

            return payload
        except jwt.InvalidTokenError:
            return None

    def attach_user_to_request(self, request, payload):
        """
        Attaches the user object to the request if the payload is valid.
        """
        try:
            user_id = payload.get("user_id")
            if user_id:
                user = User.objects.get(id=user_id)
                request.user = user
        except User.DoesNotExist:
            request.user = None

    def is_active_user(self, payload):
        try:
            user_id = payload.get("user_id")
            user = User.objects.get(id=user_id)

            if user.latest_status == "DEACTIVATED":

                return False
            else:
                return True

        except Exception as e:
            return JsonResponse({"data": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def __call__(self, request):
        # Check for access_token in cookies

        url_name = resolve(request.path).url_name
        print(url_name)

        if (
            url_name == "password-reset-confirm"
            or url_name == "auditlog-list"
            or url_name == "signup"
            or request.path.startswith("/admin/login/")
            or request.path.startswith("/admin/")
            or request.path.startswith("/api/signup")
            or request.path.startswith("/api/login")
            or request.path.startswith("/api/signup")
            or request.path.startswith("/api/logout")
            # or resolve(path=request.path).url_name in ["verify-email"]
        ):
            print("response")

            return self.get_response(request)
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")
        csrf_token = request.COOKIES.get("csrftoken")
        session = request.COOKIES.get("session")
        if not session:

            response = JsonResponse(
                {"error": "Invalid session"}, status=status.HTTP_401_UNAUTHORIZED
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            response.delete_cookie("session")
            return response
        login_log = LoginLog.objects.filter(id=session).first()
        if login_log:
            if login_log.is_revoked:
                response = JsonResponse(
                    {"error": "Your session has been revoked"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
                response.delete_cookie("access_token")
                response.delete_cookie("refresh_token")
                response.delete_cookie("session")
                return response
        if csrf_token:
            request.META["HTTP_X_CSRFTOKEN"] = csrf_token

        if access_token and refresh_token:
            try:
                # Decode the access token
                payload = self.decode_access_token(access_token)

                if payload:

                    is_active = self.is_active_user(payload=payload)
                    if not is_active:
                        return JsonResponse(
                            {
                                "error": "Your Acount is Deactivated or Blocked Contact the System Admin"
                            },
                            status=status.HTTP_401_UNAUTHORIZED,
                        )
                    # Attach user if the token is valid
                    self.attach_user_to_request(request, payload)
                exp = payload["exp"]

                # If the token is expired, attempt to refresh it
                if datetime.fromtimestamp(exp, timezone.utc) < datetime.now(
                    timezone.utc
                ):

                    try:
                        refresh = RefreshToken(refresh_token)
                        access_token = str(refresh.access_token)
                        payload = self.decode_access_token(access_token)
                        if payload:
                            is_active = self.is_active_user(payload=payload)
                            if not is_active:
                                return JsonResponse(
                                    {
                                        "error": "Your Acount is Deactivated or Blocked Contact the System Admin"
                                    },
                                    status=status.HTTP_401_UNAUTHORIZED,
                                )
                            self.attach_user_to_request(request, payload)

                        request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

                        # Set the new access token in the cookies
                        response = response = self.get_response(request)
                        response.set_cookie(
                            "access_token",
                            access_token,
                            httponly=True,
                            secure=True,
                            samesite="Strict",
                            expires=datetime.now() + timedelta(minutes=15),
                        )
                        return response

                    except TokenError:
                        # Refresh token is invalid, clear cookies and log user out
                        response = JsonResponse(
                            {"error": "Invalid refresh token"},
                            status=status.HTTP_401_UNAUTHORIZED,
                        )
                        response.delete_cookie("access_token")
                        response.delete_cookie("refresh_token")
                        response.delete_cookie("session")
                        response.delete_cookie("csrftoken")
                        return response

            except jwt.ExpiredSignatureError:

                try:
                    refresh = RefreshToken(refresh_token)
                    access_token = str(refresh.access_token)

                    payload = self.decode_access_token(access_token)
                    if payload:
                        is_active = self.is_active_user(payload=payload)
                        if not is_active:
                            return JsonResponse(
                                {
                                    "error": "Your Acount is Deactivated or Blocked Contact the System Admin"
                                },
                                status=status.HTTP_401_UNAUTHORIZED,
                            )
                        self.attach_user_to_request(request, payload)

                    request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

                    # Set the new access token in the cookies
                    response = response = self.get_response(request)
                    response.set_cookie(
                        "access_token",
                        access_token,
                        httponly=True,
                        secure=True,
                        samesite="Strict",
                        expires=datetime.now() + timedelta(days=1),
                    )
                    return response

                except TokenError:
                    # Refresh token is invalid, clear cookies and log user out
                    response = JsonResponse(
                        {"error": "Invalid refresh token"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                    response.delete_cookie("access_token")
                    response.delete_cookie("refresh_token")
                    response.delete_cookie("session")
                    response.delete_cookie("csrftoken")
                    return response
            # Access token has expired, attempt to refresh it

            except jwt.InvalidTokenError:

                # Invalid token, clear cookies and log user out
                response = JsonResponse(
                    {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
                )
                response.delete_cookie("access_token")
                response.delete_cookie("refresh_token")
                response.delete_cookie("session")
                response.delete_cookie("csrftoken")

                return response

        return self.get_response(request)
