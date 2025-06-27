from django.urls import path, include


urlpatterns = [
    path("", include("feed.urls.template_urls")),  # /feed/
    path("api/", include("feed.urls.api_urls")),  # /feed/api/
]
