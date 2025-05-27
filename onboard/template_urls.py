# onboard/template_urls.py
from django.urls import path
from .views import OnboardMainView

app_name = 'onboard_template'

urlpatterns = [
    path('', OnboardMainView.as_view(), name='onboard-main'),
]
