import uuid

from django.db import models
from django.conf import settings

from django.utils import timezone


class TravelPlan(models.Model):
    STATUS_CHOICES = [
        ("draft", "임시저장"),
        ("confirmed", "확정"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    budget_limit = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    # created_at은 생성 시 자동 기록, updated_at은 수정 시만 갱신.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            now = timezone.now()
            self.created_at = now
            self.updated_at = now
            super().save(*args, **kwargs)
        else:
            self.updated_at = timezone.now()
            super().save(*args, **kwargs)
