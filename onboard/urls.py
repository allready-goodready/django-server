# onboard/urls.py
from django.urls import path
from .views import SaveOnboardingView, LoadOnboardingView

urlpatterns = [
    path('save/', SaveOnboardingView.as_view(), name='onboarding-save'),
    path('load/', LoadOnboardingView.as_view(), name='onboarding-load'),

]
