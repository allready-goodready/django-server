from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Planner"],
    summary="여행 계획 시작 페이지",
    description="여행 계획을 생성하기 위한 시작 페이지를 렌더링합니다. Google Places API 키가 포함됩니다.",
    responses={
        200: {
            "description": "HTML 템플릿이 성공적으로 렌더링됨",
        }
    },
)
class PlanStartTemplateView(TemplateView):
    """
    여행 계획 시작 페이지를 렌더링합니다.
    Google Places API를 사용한 장소 검색 기능이 포함됩니다.
    """

    template_name = "planner/plan_start.html"
    permission_classes = [IsAuthenticated]  # 기존 permission 유지

    def dispatch(self, request, *args, **kwargs):
        """permission_classes를 확인하는 dispatch 메서드"""
        # REST Framework의 permission_classes 확인
        for permission_class in self.permission_classes:
            permission = permission_class()
            if not permission.has_permission(request, self):
                from django.contrib.auth.views import redirect_to_login

                return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """템플릿에 전달할 컨텍스트 데이터를 반환합니다."""
        context = super().get_context_data(**kwargs)
        context["GOOGLE_PLACES_API_KEY"] = settings.GOOGLE_API_KEY  # 기존 API 키 유지
        return context
