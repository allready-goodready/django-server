# onboard/views/exchange_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from onboard.services.exchange_api import get_exchange_rate
from drf_spectacular.utils import extend_schema

@extend_schema(
    parameters=[
        {
            "name": "base",
            "required": False,
            "type": str,
            "description": "기준 통화 (기본값: KRW)"
        },
        {
            "name": "target",
            "required": False,
            "type": str,
            "description": "변환할 통화 (기본값: USD)"
        }
    ],
    responses=200,
    description="기준 통화와 대상 통화 간의 실시간 환율 정보 조회"
)
class ExchangeRateAPI(APIView):
    def get(self, request):
        target = request.GET.get("target", "USD")
        base = request.GET.get("base", "KRW")

        result = get_exchange_rate(base=base, target=target)
        return Response(result)
