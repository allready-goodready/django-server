from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from planner.models import TravelPlan
from .services import get_nearest_airport


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
