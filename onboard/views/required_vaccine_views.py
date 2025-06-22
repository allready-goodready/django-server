# onboard/views/required_vaccine_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from onboard.models.vaccine_models import RequiredVaccine
from onboard.models.country_models import Country
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

@extend_schema(
    parameters=[
        OpenApiParameter(
            name='country_code',
            type=str,
            description='국가 코드 (예: US, JP, KR)',
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(description="요청한 국가에 필요한 백신 리스트"),
        404: OpenApiResponse(description="국가 정보가 없을 때")
    }
)

class RequiredVaccineListView(APIView):
    def get(self, request):
        country_code = request.GET.get("country_code")
        if not country_code:
            return Response({"error": "country_code query parameter is required"}, status=400)
        
        try:
            country = Country.objects.get(code=country_code.upper())
        except Country.DoesNotExist:
            return Response({"error": "Invalid country_code"}, status=404)
        
        required_vaccines = RequiredVaccine.objects.filter(country=country).select_related("vaccine")
        vaccine_list = [rv.vaccine.name for rv in required_vaccines]

        return Response({
            "country": country.name,
            "required_vaccines": vaccine_list
        })
