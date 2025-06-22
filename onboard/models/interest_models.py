# onboard/models/interest_models.py

from django.db import models

class InterestCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class InterestItem(models.Model):
    category = models.ForeignKey(
        InterestCategory,
        on_delete=models.CASCADE,
        related_name='items'
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
