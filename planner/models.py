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


class Location(models.Model):
    TYPE_ORIGIN = "origin"
    TYPE_DESTINATION = "destination"
    TYPE_CHOICES = [
        (TYPE_ORIGIN, "출발지"),
        (TYPE_DESTINATION, "목적지"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        TravelPlan, on_delete=models.CASCADE, related_name="locations"
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        help_text="예: “서울역”, “제주공항” 등. 외부 API에서 받은 장소명이 있으면 저장",
    )
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, help_text="origin 또는 destination 중 하나"
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        help_text="외부 API(예: Geoapify)에서 받은 전체 주소 문자열",
    )
    lat = models.FloatField(help_text="위도(latitude)")
    lng = models.FloatField(help_text="경도(longitude)")
    place_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Googleplaces API에서 제공하는 고유 장소 ID",
    )
