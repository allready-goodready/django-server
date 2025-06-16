from django.urls import path
from .views import AirportNearOriginAPIView, AirportNearDestAPIView

urlpatterns = [
    # 출발지 근처 공항 조회
    path(
        "airports/from/",
        AirportNearOriginAPIView.as_view(),
        name="api_flight_airport_near_origin",
    ),
    # 도착지 근처 공항 조회
    path(
        "airports/to/",
        AirportNearDestAPIView.as_view(),
        name="api_flight_airport_near_dest",
    ),
]
