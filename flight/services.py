from django.conf import settings
from amadeus import Client, ResponseError
import logging
from datetime import datetime

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


def search_flight_offers(
    origin, destination, depart_date, return_date, adults=1, max=20
):
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=depart_date,
            returnDate=return_date,
            adults=adults,
            max=max,
        )
        return response.data
    except ResponseError as e:
        logger.error("Amadeus Error in search_flight_offers: %s", e)
    except Exception as e:
        logger.exception("Unexpected error in search_flight_offers: %s", e)
    return []


def prioritize_offers(offers):
    def parse_time(dt):
        return datetime.fromisoformat(dt)

    def is_return_round(o):
        return len(o.get("itineraries", [])) == 2

    def key_fn(o):
        out_dep = parse_time(o["itineraries"][0]["segments"][0]["departure"]["at"])
        ret_arr = parse_time(o["itineraries"][1]["segments"][-1]["arrival"]["at"])
        price = float(o["price"]["total"])
        # PT#H#M 형식에서 시간과 분을 추출하여 총 분 산정
        duration = sum(
            int(seg["duration"].replace("PT", "").replace("H", "").replace("M", ""))
            for itin in o["itineraries"]
            for seg in itin["segments"]
        )
        stops = sum(len(itin["segments"]) - 1 for itin in o["itineraries"])
        return (
            0 if is_return_round(o) else 1,
            out_dep,
            -ret_arr.timestamp(),
            price,
            duration,
            stops,
        )

    return sorted(offers, key=key_fn)
