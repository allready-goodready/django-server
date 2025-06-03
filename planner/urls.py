from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TravelPlanViewSet, DestinationViewSet

app_name = "planner"

router = DefaultRouter()
router.register("travelplan", TravelPlanViewSet, basename="travelplan")
router.register("destination", DestinationViewSet, basename="destination")

urlpatterns = [
    path("", include(router.urls)),
]
