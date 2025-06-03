# views.py

from rest_framework import permissions, viewsets

from event.models.event import Calendar, Event
from event.serializers.event import CalendarSerializer, EventSerializer


class CalendarViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Calendar.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user).select_related("calendar")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
