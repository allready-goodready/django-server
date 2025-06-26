# onboard/views/exchange_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from onboard.services.exchange_api import get_exchange_rate
from onboard.models import Country

from drf_spectacular.utils import extend_schema, OpenApiParameter


@extend_schema(
    parameters=[
        OpenApiParameter(name="base", type=str, required=False, description="기준 통화 (기본값: KRW)"),
        OpenApiParameter(name="country_code", type=str, required=True, description="대상 국가 코드 (예: JP, US 등)"),
    ],
    responses=200,
    description="기준 통화와 대상 국가의 통화 간 실시간 환율 정보 조회"
)
class ExchangeRateView(APIView):
    def get(self, request):
        base = request.GET.get("base", "KRW")
        country_code = request.GET.get("country_code")

        try:
            country = Country.objects.get(code=country_code)
            target = country.currency_code or "USD"
        except Country.DoesNotExist:
            target = "USD"

        result = get_exchange_rate(base, target)
        return Response(result)


@extend_schema(
    parameters=[
        OpenApiParameter(name="country_code", type=str, required=True, description="국가 코드")
    ],
    responses=200,
    description="국가별 현지 팁 정보 반환 (정적 예시)"
)
class ExtraInfoView(APIView):
    def get(self, request):
        # 나중에 country_code에 따라 분기할 수도 있음
        data = {
            'tip1': '공공장소에서는 조용히',
            'tip2': '왼쪽으로 걷기'
        }
        return Response(data, status=status.HTTP_200_OK)


def extra_info_page(request):
    return render(request, "onboard/extra_info.html")
