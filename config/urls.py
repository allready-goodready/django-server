# config/urls.py

from django.contrib import admin 
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("onboard/", include("onboard.urls.template_urls")),
    path("api/onboard/", include("onboard.urls.api_urls")),
    path("api/schema/", include("onboard.urls.schema_urls")),
]
