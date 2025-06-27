from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status, mixins, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from config.permissions import IsOwnerOrReadOnly
from config.paginations import DefaultPagination

# drf-spectacular 문서화 데코레이터
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import TravelPlan, Location
from .serializers import (
    TravelPlanDraftSerializer,
    TravelPlanUpdateSerializer,
    TravelPlanConfirmSerializer,
    LocationModelSerializer,
)
from .services import confirm_travelplan, upsert_location


@extend_schema_view(
    list=extend_schema(
        tags=["Planner"],
        summary="여행 계획 목록 조회",
        description="사용자의 모든 여행 계획을 조회합니다.",
    ),
    create=extend_schema(
        tags=["Planner"],
        summary="여행 계획 생성",
        description="새로운 여행 계획을 Draft 상태로 생성합니다.",
    ),
    retrieve=extend_schema(
        tags=["Planner"],
        summary="여행 계획 상세 조회",
        description="특정 여행 계획의 상세 정보를 조회합니다.",
    ),
    update=extend_schema(
        tags=["Planner"],
        summary="여행 계획 수정",
        description="Draft 상태의 여행 계획을 수정합니다.",
    ),
    partial_update=extend_schema(
        tags=["Planner"],
        summary="여행 계획 부분 수정",
        description="Draft 상태의 여행 계획을 부분적으로 수정합니다.",
    ),
    destroy=extend_schema(
        tags=["Planner"],
        summary="여행 계획 삭제",
        description="여행 계획을 삭제합니다.",
    ),
)
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

    @extend_schema(
        tags=["Planner"],
        summary="여행 계획 확정",
        description="Draft 상태의 여행 계획을 최종 확정(confirmed) 상태로 변경합니다.",
        request=None,
        responses={
            200: TravelPlanDraftSerializer,
            400: {"description": "확정할 수 없는 상태 (필수 정보 누락 등)"},
        },
    )
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


@extend_schema_view(
    list=extend_schema(
        tags=["Planner"],
        summary="목적지 목록 조회",
        description="사용자의 여행 계획에 등록된 목적지 목록을 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="plan",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description="여행 계획 ID로 필터링",
            ),
        ],
    ),
    create=extend_schema(
        tags=["Planner"],
        summary="목적지 추가/수정",
        description="여행 계획에 목적지를 추가하거나 수정합니다. 같은 place_id가 있으면 수정, 없으면 추가됩니다.",
        examples=[
            OpenApiExample(
                "목적지 추가 예시",
                value={
                    "plan": "550e8400-e29b-41d4-a716-446655440000",
                    "place_id": "ChIJ4QOYM4GhfDUR1kPR_tLW1A0",
                    "name": "제주도",
                    "address": "제주특별자치도",
                    "lat": 33.4996,
                    "lng": 126.5312,
                },
                request_only=True,
            )
        ],
    ),
)
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


@extend_schema_view(
    list=extend_schema(
        tags=["Planner"],
        summary="출발지 목록 조회",
        description="사용자의 여행 계획에 등록된 출발지 목록을 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="plan",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description="여행 계획 ID로 필터링",
            ),
        ],
    ),
    create=extend_schema(
        tags=["Planner"],
        summary="출발지 추가/수정",
        description="여행 계획에 출발지를 추가하거나 수정합니다. 같은 place_id가 있으면 수정, 없으면 추가됩니다.",
        examples=[
            OpenApiExample(
                "출발지 추가 예시",
                value={
                    "plan": "550e8400-e29b-41d4-a716-446655440000",
                    "place_id": "ChIJwULG5WSOdDURStClk2-oPNE",
                    "name": "인천국제공항",
                    "address": "인천광역시 중구 공항로 272",
                    "lat": 37.4449,
                    "lng": 126.4656,
                },
                request_only=True,
            )
        ],
    ),
)
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
