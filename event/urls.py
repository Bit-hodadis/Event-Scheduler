# urls.py

from rest_framework.routers import DefaultRouter

from event.views import CalendarViewSet, EventViewSet

router = DefaultRouter()
router.register(r"calendars", CalendarViewSet, basename="calendar")
router.register(r"events", EventViewSet, basename="event")

urlpatterns = router.urls
