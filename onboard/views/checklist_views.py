# onboard/views/checklist_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from onboard.models import ChecklistItem
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from onboard.models import UserChecklist
from onboard.serializers.checklist import UserChecklistSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from onboard.models.checklist_models import ChecklistItem
from onboard.serializers.checklist import ChecklistDetailSerializer

@extend_schema(
    summary="체크리스트 항목 상세 조회",
    description="ID를 기반으로 체크리스트 항목의 제목과 상세 설명을 반환합니다.",
)
class ChecklistDetailAPI(RetrieveAPIView):
    queryset = ChecklistItem.objects.all()
    serializer_class = ChecklistDetailSerializer
    lookup_field = 'id'


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
    
class SaveChecklistAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UserChecklistSerializer)
    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = UserChecklistSerializer(data=data)
        if serializer.is_valid():
            checklist, created = UserChecklist.objects.update_or_create(
                user=request.user,
                country=data['country'],
                req_id=data['req_id'],
                defaults={'is_checked': data['is_checked']}
            )
            return Response(UserChecklistSerializer(checklist).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoadChecklistAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=UserChecklistSerializer(many=True))
    def get(self, request):
        qs = UserChecklist.objects.filter(user=request.user)
        serializer = UserChecklistSerializer(qs, many=True)
        return Response(serializer.data)
