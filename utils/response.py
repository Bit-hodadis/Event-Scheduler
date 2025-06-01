from rest_framework.response import Response


def success_response(data=None, message="Success", status=200):
    """
    Generate a standardized success response.
    """
    return Response({"success": True, "message": message, "data": data}, status=status)


def error_response(errors=None, message="An error occurred", status=400):
    """
    Generate a standardized error response.
    """
    return Response(
        {"success": False, "message": message, "errors": errors}, status=status
    )
