from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from config.permissions import IsOwnerOrReadOnly
from config.paginations import DefaultPagination

from .models import TravelPlan
from .serializers import (
    TravelPlanDraftSerializer,
    TravelPlanUpdateSerializer,
    TravelPlanConfirmSerializer,
)
from .services import confirm_travelplan


class TravelPlanViewSet(viewsets.ModelViewSet):
    """
    TravelPlan 생성, 조회, 수정, 삭제, 그리고 Confirm(최종 확정) 기능을 모두 제공합니다.

    - create → TravelPlanDraftSerializer 사용 (status='draft' 로 생성)
    - list/retrieve → TravelPlanDraftSerializer 사용 (created_at, updated_at, status 포함 출력)
    - update/partial_update → TravelPlanUpdateSerializer 사용 (draft 상태일 때만 수정 허용)
    - destroy → TravelPlan 인스턴스 삭제 (draft/confirmed 상관없이, 단 필요 시 권한 추가 가능)
    - confirm (커스텀 액션) → TravelPlanConfirmSerializer 사용, services.confirm_travelplan 호출
    """

    queryset = TravelPlan.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = DefaultPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "start_date", "end_date", "title"]
    ordering = ["created_at"]

    def get_serializer_class(self):
        # action에 따라 사용하는 Serializer를 분기
        if self.action == "create":
            return TravelPlanDraftSerializer
        elif self.action in ["update", "partial_update"]:
            return TravelPlanUpdateSerializer
        # list, retrieve, destroy 등 그 외에는 DraftSerializer(읽기용) 사용
        return TravelPlanDraftSerializer

    def perform_create(self, serializer):
        # create 시 status='draft'로 저장하는 로직은 Serializer.create() 내부에서 처리됨
        serializer.save()

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        """
        POST /api/travel-plans/{pk}/confirm/
        Draft 상태의 TravelPlan을 최종 확정(confirmed)으로 변경합니다.

        - TravelPlanConfirmSerializer로 간단히 통과시킨 뒤,
          services.confirm_travelplan() 을 호출하여 상태 변경 및 필수 관계 검증 수행
        - 성공 시, 변경된 TravelPlan 데이터를 다시 TravelPlanDraftSerializer로 직렬화하여 반환
        """
        plan = self.get_object()  # request.user 소유 & pk 검사 완료된 인스턴스

        serializer = TravelPlanConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            confirmed_plan = confirm_travelplan(plan.id)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        read_serializer = TravelPlanDraftSerializer(
            confirmed_plan, context={"request": request}
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)
