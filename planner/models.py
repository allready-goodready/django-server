import uuid

from django.db import models
from django.contrib.auth import get_user_model


class TravelPlan(models.Model):
    STATUS_CHOICES = [
        ("draft", "임시저장"),
        ("confirmed", "확정"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    budget_limit = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
