from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from users.serializers.user import UserSerializer


class UserProfileViewSet(viewsets.ViewSet):

    def profile(self, request):
        user = request.user  # Get the logged-in user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update_profile(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = serializer.data
            user = request.user
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
