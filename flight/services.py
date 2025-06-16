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
    api test 환경에서는 다음 국가에 대해서만 조회 가능합니다.
    United States, Spain, United Kingdom, Germany and India
    """
    try:
        response = amadeus.reference_data.locations.airports.get(
            latitude=lat,
            longitude=lon,
            radius=500,
            sort="distance",
        )
        data = response.data
        if data and len(data) > 0:
            airport = data[0]
            return {
                "iata": airport.get("iataCode"),
                "name": airport.get("name", ""),
            }
    except ResponseError as e:
        logger.error("Amadeus Error in get_nearest_airport: %s", e)
    except Exception as e:
        logger.exception("Unexpected error in get_nearest_airport: %s", e)
    return None
