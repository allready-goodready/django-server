# onboard/views/checklist_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from onboard.models import ChecklistItem
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['req_id', 'feature', 'message', 'fallback_message']

@extend_schema(
    parameters=[
        OpenApiParameter(
            name="country_code",
            required=True,
            type=str,
            description="국가 코드 (예: JP, US)"
        )
    ],
    responses=ChecklistItemSerializer(many=True)
)
class ChecklistAPIView(APIView):
    def get(self, request):
        country_code = request.query_params.get("country_code")
        if not country_code:
            return Response({"detail": "country_code parameter is required"}, status=400)

        items = ChecklistItem.objects.filter(country_code=country_code)
        serializer = ChecklistItemSerializer(items, many=True)
        return Response(serializer.data)
