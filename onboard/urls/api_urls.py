# onboard/urls/api_urls.py

from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from onboard.views import (
    SaveOnboardingView,
    LoadOnboardingView,
    OnboardingOptionsView,
    CountryListView,
    InterestItemListView,
)
from onboard.views.checklist_views import ChecklistAPIView  
from onboard.views.exchange_views import ExchangeRateAPI
from onboard.views.vaccine_views import VaccineInfoAPI
from onboard.views.required_vaccine_views import RequiredVaccineListView

urlpatterns = [
    # 온보딩 API
    path("save/", SaveOnboardingView.as_view(), name="onboarding-save"),
    path("load/", LoadOnboardingView.as_view(), name="onboarding-load"),
    path("options/", OnboardingOptionsView.as_view(), name="onboarding-options"),

    # 리스트 API
    path("countries/", CountryListView.as_view(), name="country-list"),
    path("interests/", InterestItemListView.as_view(), name="interest-list"),

    # 외부 정보 API
    path("exchange-rate/", ExchangeRateAPI.as_view(), name="exchange-rate"),
    path("vaccine-info/", VaccineInfoAPI.as_view(), name="vaccine-info"),
    path("required-vaccines/", RequiredVaccineListView.as_view(), name="required-vaccines"),
    path("checklist/", ChecklistAPIView.as_view(), name="checklist"),

    # Swagger 문서
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
