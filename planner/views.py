from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from config.permissions import IsOwnerOrReadOnly
from config.paginations import DefaultPagination


from .models import TravelPlan
from .serializers import TravelPlanSerializer


class TravelPlanViewSet(viewsets.ModelViewSet):
    """
    여행 계획 CRUD + 리스트/단일 조회 뷰셋
    - 본인 계획만 수정/삭제 가능
    """

    queryset = TravelPlan.objects.all()
    serializer_class = TravelPlanSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = DefaultPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "start_date", "end_date", "title"]
    ordering = ["created_at"]

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="my-plans",
    )
    def my_plans(self, request):
        """
        GET /travel-plans/my-plans/
        로그인 사용자(request.user)가 생성한 여행 계획만 조회
        """
        qs = self.queryset.filter(user=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
