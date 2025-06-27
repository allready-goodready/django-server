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
            currencyCode="KRW",
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

    def is_round_trip(o):
        return len(o.get("itineraries", [])) == 2

    def key_fn(o):
        out_dt = parse_time(o["itineraries"][0]["segments"][0]["departure"]["at"])
        ret_dt = parse_time(o["itineraries"][1]["segments"][-1]["arrival"]["at"])
        price = float(o["price"]["total"])
        # 비행 시간 총 분 계산 (PT#H#M 형태에서 시간·분 분리)
        total_minutes = 0
        for itin in o["itineraries"]:
            for seg in itin["segments"]:
                dur = seg.get("duration", "")
                dur = dur.replace("PT", "")
                hours, minutes = 0, 0
                if "H" in dur:
                    h_part, m_part = dur.split("H")
                    hours = int(h_part)
                    if m_part.endswith("M"):
                        minutes = int(m_part[:-1])
                elif dur.endswith("M"):
                    minutes = int(dur[:-1])
                total_minutes += hours * 60 + minutes
        stops = sum(len(itin["segments"]) - 1 for itin in o["itineraries"])
        return (
            0 if is_round_trip(o) else 1,
            out_dt,
            -ret_dt.timestamp(),
            price,
            total_minutes,
            stops,
        )

    return sorted(offers, key=key_fn)


def get_airlines_info(codes):
    """
    IATA 코드 리스트(codes)에 대해 Amadeus Reference Data API 호출.
    반환: {'KE': {'commonName':'Korean Air', …}, …}
    """
    try:
        resp = amadeus.reference_data.airlines.get(airlineCodes=",".join(codes))
        data = resp.data or []
        return {
            a["iataCode"]: {
                "commonName": a.get("commonName"),
                "businessName": a.get("businessName"),
            }
            for a in data
        }
    except ResponseError as e:
        logger.error("Error fetching airlines info: %s", e)
        return {}


def book_flight(
    offer_snapshot, travelers, remarks=None, ticketing_agreement=None, contacts=None
):
    """
    offer_snapshot: selected_offer_snapshot (dict)
    travelers: list of traveler dicts matching API 스펙
    remarks: {"general": [...]}
    ticketing_agreement: {"option": "...", "delay": "..."}
    contacts: list of contact dicts matching API 스펙
    """
    flight_offer = offer_snapshot.copy()
    flight_offer.setdefault("type", "flight-offer")

    data = {
        "type": "flight-order",
        "flightOffers": [flight_offer],
        "travelers": travelers,
    }
    if remarks:
        data["remarks"] = remarks
    if ticketing_agreement:
        data["ticketingAgreement"] = ticketing_agreement
    if contacts:
        data["contacts"] = contacts

    body = {"data": data}

    try:
        response = amadeus.client.post("/v1/booking/flight-orders", body)
        return response.data
    except ResponseError as error:
        print("Amadeus booking error:", error, getattr(error, "response", None))
        raise
