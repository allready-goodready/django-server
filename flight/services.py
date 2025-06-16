from django.conf import settings
from amadeus import Client, ResponseError
import logging

amadeus = Client(
    client_id=settings.AMADEUS_CLIENT_ID, client_secret=settings.AMADEUS_CLIENT_SECRET
)

logger = logging.getLogger(__name__)


def get_nearest_airport(lat, lon):
    """
    주어진 위경도(lat, lon)로부터 가장 가까운 공항 정보를 반환합니다.
    반환값 예시: {"iata": "ICN", "name": "Incheon International Airport"}
    실패 시 None을 반환합니다.
    """
    try:
        response = amadeus.reference_data.locations.airports.get(
            latitude=lat,
            longitude=lon,
            radius=5000,
            page_limit=1,
        )
        data = response.data
        if data and len(data) > 0:
            airport = data[0]
            return {
                "iata": airport.get("iataCode"),
                "name": airport.get("name", ""),
            }
    except ResponseError as e:
        logger.error("Amadeus API Error in get_nearest_airport: %s", e)
    except Exception as e:
        logger.exception("Unexpected error in get_nearest_airport: %s", e)
    return None
