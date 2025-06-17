from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from planner.models import TravelPlan
from .services import get_nearest_airport, search_flight_offers, prioritize_offers


class FlightSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_id = request.query_params.get("plan_id")
        adults = request.query_params.get("adults", 1)
        earliest_dep = request.query_params.get("earliest_dep")
        latest_arr = request.query_params.get("latest_arr")

        plan = get_object_or_404(TravelPlan, id=plan_id, user=request.user)
        fs = get_nearest_airport(
            plan.locations.filter(type="origin").first().latitude,
            plan.locations.filter(type="origin").first().longitude,
        )
        origin_iata = fs["iata"] if fs else None
        ds = get_nearest_airport(
            plan.locations.filter(type="destination").first().latitude,
            plan.locations.filter(type="destination").first().longitude,
        )
        dest_iata = ds["iata"] if ds else None
        if not origin_iata or not dest_iata:
            return Response({"error": "Airport info missing."}, status=400)

        offers = search_flight_offers(
            origin_iata,
            dest_iata,
            plan.start_date.isoformat(),
            plan.end_date.isoformat(),
            adults=int(adults),
        )
        # 시간 필터
        if earliest_dep:
            offers = [
                o
                for o in offers
                if o["itineraries"][0]["segments"][0]["departure"]["at"].split("T")[1]
                >= earliest_dep
            ]
        if latest_arr:
            offers = [
                o
                for o in offers
                if o["itineraries"][1]["segments"][-1]["arrival"]["at"].split("T")[1]
                <= latest_arr
            ]

        # 기본값 선정
        default = None
        if offers:
            prioritized = prioritize_offers(offers)
            default = prioritized[0]

        return Response({"offers": offers, "default_offer": default})


class AirportNearOriginAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_id = request.query_params.get("plan_id")
        plan = get_object_or_404(TravelPlan, id=plan_id, user=request.user)
        origin_loc = plan.locations.filter(type="origin").first()
        if not origin_loc:
            return Response({"error": "Origin location not found."}, status=404)

        result = get_nearest_airport(origin_loc.lat, origin_loc.lng)
        if not result:
            return Response({"error": "Nearest airport not found."}, status=400)
        return Response(result)


class AirportNearDestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_id = request.query_params.get("plan_id")
        plan = get_object_or_404(TravelPlan, id=plan_id, user=request.user)
        dest_loc = plan.locations.filter(type="destination").first()
        if not dest_loc:
            return Response({"error": "Destination location not found."}, status=404)

        result = get_nearest_airport(dest_loc.latitude, dest_loc.longitude)
        if not result:
            return Response({"error": "Nearest airport not found."}, status=400)
        return Response(result)
