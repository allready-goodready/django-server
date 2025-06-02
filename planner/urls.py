from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TravelPlanViewSet

app_name = "planner"

router = DefaultRouter()
router.register("travelplan", TravelPlanViewSet, basename="travelplan")

urlpatterns = [
    path("", include(router.urls)),
]
