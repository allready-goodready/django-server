from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("feed/", include("feed.urls")),
    path("api/plan/", include("planner.urls", namespace="planner_api")),
    path("api/flight/", include("flight.urls", namespace="flight")),
    path("plan/", include("planner.template_urls", namespace="planner")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
