from django.urls import path
from django.conf import settings
from .template_views import PlanStartTemplateView

app_name = "planner"

urlpatterns = [
    path(
        "start/",
        PlanStartTemplateView.as_view(),
        name="plan_start",
    ),
    # (추가적인 템플릿 URL이 있으면 여기에 계속 작성)
]
