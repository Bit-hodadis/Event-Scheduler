from rest_framework.exceptions import APIException
from rest_framework.viewsets import ModelViewSet

from utils.response import error_response, success_response


class BaseViewSet(ModelViewSet):
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return success_response(
                data=response.data, message="Created successfully", status=201
            )
        except APIException as e:
            return error_response(
                errors=e.detail,
                message="Failed to create resource",
                status=e.status_code,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
            return success_response(
                data=response.data, message="Data retrieved successfully"
            )
        except APIException as e:
            return error_response(
                errors=e.detail,
                message="Failed to retrieve resource",
                status=e.status_code,
            )

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            return success_response(
                data=response.data, message="Data listed successfully"
            )
        except APIException as e:
            return error_response(
                errors=e.detail,
                message="Failed to list resources",
                status=e.status_code,
            )

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return success_response(data=response.data, message="Updated successfully")
        except APIException as e:
            return error_response(
                errors=e.detail,
                message="Failed to update resource",
                status=e.status_code,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, *args, **kwargs)
            return success_response(message="Deleted successfully", status=204)
        except APIException as e:
            return error_response(
                errors=e.detail,
                message="Failed to delete resource",
                status=e.status_code,
            )
