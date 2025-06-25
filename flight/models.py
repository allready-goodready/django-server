from django.db import models
import uuid

from planner.models import TravelPlan


class FlightSelection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.OneToOneField(
        TravelPlan, on_delete=models.CASCADE, related_name="flight_selection"
    )
    departure_iata = models.CharField(max_length=3)
    arrival_iata = models.CharField(max_length=3)
    offers_data = models.JSONField(null=True, blank=True)
    selected_offer_id = models.CharField(max_length=100, null=True, blank=True)
    selected_offer_snapshot = models.JSONField(null=True, blank=True)
    last_ticketing_date = models.DateField(null=True, blank=True)
    selected_at = models.DateTimeField(auto_now_add=True)
    price_data = models.JSONField(null=True, blank=True)
    booking_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
