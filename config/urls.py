from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/onboard/', include('onboard.urls')),
    path('onboard/', include('onboard.template_urls')),
]
