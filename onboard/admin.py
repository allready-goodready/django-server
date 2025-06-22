from django.contrib import admin
from .models import (
    Country, Vaccine, RequiredVaccine,
    InterestCategory, InterestItem,
    UserOnboarding
)

admin.site.register(Country)
admin.site.register(Vaccine)
admin.site.register(RequiredVaccine)
admin.site.register(InterestCategory)
admin.site.register(InterestItem)
admin.site.register(UserOnboarding)
