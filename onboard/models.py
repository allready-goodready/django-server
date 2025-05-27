# onboard/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class InterestCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class InterestItem(models.Model):
    category = models.ForeignKey(InterestCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class UserOnboarding(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    countries = models.ManyToManyField(Country)
    interest_items = models.ManyToManyField(InterestItem)

    def __str__(self):
        return f"{self.user.username}'s Onboarding"
