from django.urls import path
from onboard.views import onboarding_views
from onboard.views.exchange_views import extra_info_page 

urlpatterns = [
    path('select-country/', onboarding_views.select_country, name='select_country'),
    path('checklist/', onboarding_views.checklist, name='checklist'),
    path('extra-info/', extra_info_page, name='extra_info'),


]
