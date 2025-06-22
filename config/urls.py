# config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("onboard/", include("onboard.urls.urls")),
    path("api/schema/", include("onboard.urls.schema_urls")), 
]
