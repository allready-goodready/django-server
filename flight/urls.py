from django.urls import path
from .views import FlightSearchAPIView, AirportNearOriginAPIView, AirportNearDestAPIView

app_name = "flight"

urlpatterns = [
    path(
        "airports/from/",
        AirportNearOriginAPIView.as_view(),
        name="api_flight_airport_near_origin",
    ),
    path(
        "airports/to/",
        AirportNearDestAPIView.as_view(),
        name="api_flight_airport_near_dest",
    ),
    path("search/", FlightSearchAPIView.as_view(), name="api_flight_search"),
]
