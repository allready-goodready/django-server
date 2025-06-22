# onboard/models/vaccine_models.py

from django.db import models
from .country_models import Country

class Vaccine(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class RequiredVaccine(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('country', 'vaccine')  # 중복 방지

    def __str__(self):
        return f"{self.country.name} - {self.vaccine.name}"
