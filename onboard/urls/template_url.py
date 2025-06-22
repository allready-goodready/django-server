# onboard/urls/template_urls.py

from django.urls import path
from onboard.views import OnboardMainView

urlpatterns = [
    path("", OnboardMainView.as_view(), name="onboard-main"),
]
