from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TravelPlanViewSet

app_name = "planner_api"

router = DefaultRouter()
router.register(r"travel-plans", TravelPlanViewSet, basename="travelplan")

urlpatterns = [
    path(
        "/start/",
        TravelPlanViewSet.as_view({"get": "list", "post": "create"}),
        name="api_plan_start",
    ),
    path(
        "/my-plans/",
        TravelPlanViewSet.as_view({"get": "my_plans"}),
        name="api_plan_my_plans",
    ),
    # /api/travel-plans/… 기본 CRUD
    path("", include(router.urls)),
]
