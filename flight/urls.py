from django.urls import path
from .views import (
    FlightSearchAPIView,
    FlightCandidatesAPIView,
    AirportNearOriginAPIView,
    AirportNearDestAPIView,
    FlightSelectAPIView,
    FlightBookAPIView,
)

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
    path(
        "candidates/", FlightCandidatesAPIView.as_view(), name="api_flight_candidates"
    ),
    path("select/", FlightSelectAPIView.as_view(), name="api_flight_select"),
    path("book/", FlightBookAPIView.as_view(), name="api_flight_book"),
]
