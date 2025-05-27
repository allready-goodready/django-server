# onboard/admin.py
from django.contrib import admin
from .models import Country, InterestCategory, InterestItem, UserOnboarding

admin.site.register(Country)
admin.site.register(InterestCategory)
admin.site.register(InterestItem)
admin.site.register(UserOnboarding)
