from django.db import models
from django.contrib.auth import get_user_model
from .country_models import Country
from .interest_models import InterestItem

User = get_user_model()

class UserOnboarding(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    countries = models.ManyToManyField(Country)
    interest_items = models.ManyToManyField(InterestItem)

    def __str__(self):
        return f"{self.user.username}'s Onboarding"
