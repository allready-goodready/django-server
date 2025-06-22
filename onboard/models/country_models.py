from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)  # 예: "US", "KR"
    currency_code = models.CharField(max_length=10, default="USD")

    def __str__(self):
        return f"{self.name} ({self.code})"
