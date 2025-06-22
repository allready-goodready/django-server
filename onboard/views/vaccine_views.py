from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter

# 응답용 Serializer 정의
class VaccineInfoSerializer(serializers.Serializer):
    country = serializers.CharField()
    required_vaccines = serializers.ListField(child=serializers.CharField())

@extend_schema(
    parameters=[
        OpenApiParameter(
            name="country_code", 
            required=True, 
            type=str, 
            description="국가 코드 (예: US, JP)"
        )
    ],
    responses=VaccineInfoSerializer
)
class VaccineInfoAPI(APIView):
    def get(self, request):
        country_code = request.query_params.get("country_code", "")
        # 예시 응답
        return Response({
            "country": "미국",
            "required_vaccines": ["홍역·볼거리·풍진(MMR) 백신"]
        })
