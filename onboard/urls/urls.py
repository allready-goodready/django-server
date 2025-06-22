# onboard/urls/urls.py

from django.urls import path, include

urlpatterns = [
    path("", include("onboard.urls.template_urls")),
    path("api/", include("onboard.urls.api_urls")),
]
