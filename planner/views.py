from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status, mixins, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from config.permissions import IsOwnerOrReadOnly
from config.paginations import DefaultPagination

from .models import TravelPlan, Location
from .serializers import (
    TravelPlanDraftSerializer,
    TravelPlanUpdateSerializer,
    TravelPlanConfirmSerializer,
    LocationModelSerializer,
)
from .services import confirm_travelplan, upsert_location


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
        POST /api/plan/travelplans/{pk}/confirm/
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


class DestinationViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """
    - GET  /api/plan/destination/         → 현재 사용자 소유 TravelPlan에 연결된
                                            type='destination'인 Location 목록 조회
    - POST /api/plan/destination/         → Destination upsert
       • 요청바디:
         {
             "plan": "<plan_uuid>",
             "place_id": "...",
             "name": "...",
             "address": "...",
             "lat": 12.34,
             "lng": 56.78
         }
       • 내부에서 `type="destination"`을 자동 주입 → upsert_location 호출
    """

    serializer_class = LocationModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 모든 Location 중 type='destination'인 데이터 반환
        queryset = Location.objects.filter(type="destination")
        # (선택) 쿼리 파라미터로 plan=<plan_uuid>를 받으면, 해당 Plan에만 한정
        plan_id = self.request.query_params.get("plan")
        if plan_id:
            queryset = queryset.filter(plan__id=plan_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """
        POST /api/plan/destination/
        - body에 "plan": "<plan_uuid>" 필수
        - type은 내부에서 "destination"으로 주입
        """
        user = request.user
        data = request.data.copy()

        # 1) plan 필수 체크
        plan_id = data.get("plan")
        if not plan_id:
            return Response(
                {"plan": "이 필드는 반드시 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2) TravelPlan 소유권 확인
        travel_plan = get_object_or_404(TravelPlan, pk=plan_id, user=user)

        # 3) 타입 강제 주입
        data["type"] = "destination"

        # 4) serializer 검사 (plan은 write_only, type도 write_only이므로 data에 담아줘야 통과)
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # 5) upsert_location 호출
        location, created = upsert_location(
            user=user, plan_id=travel_plan.id, validated_data=serializer.validated_data
        )

        # 6) 응답
        output = self.get_serializer(location).data
        output.pop("plan", None)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(output, status=status_code)


class OriginViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """
    - GET  /api/plan/origin/         → 현재 사용자 소유 TravelPlan에 연결된
                                        type='origin'인 Location 목록 조회
    - POST /api/plan/origin/         → Origin upsert
       • 요청바디:
         {
             "plan": "<plan_uuid>",
             "place_id": "...",
             "name": "...",
             "address": "...",
             "lat": 12.34,
             "lng": 56.78
         }
       • 내부에서 `type="origin"`을 자동 주입 → upsert_location 호출
    """

    serializer_class = LocationModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Location.objects.filter(type="origin")
        plan_id = self.request.query_params.get("plan")
        if plan_id:
            queryset = queryset.filter(plan__id=plan_id)
        return queryset

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()

        plan_id = data.get("plan")
        if not plan_id:
            return Response(
                {"plan": "이 필드는 반드시 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        travel_plan = get_object_or_404(TravelPlan, pk=plan_id, user=user)

        data["type"] = "origin"

        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        location, created = upsert_location(
            user=user, plan_id=travel_plan.id, validated_data=serializer.validated_data
        )

        output = self.get_serializer(location).data
        output.pop("plan", None)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(output, status=status_code)
