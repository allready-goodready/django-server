from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/plan/", include("planner.urls", namespace="planner_api")),
]
