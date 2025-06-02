from django.urls import path
from django.views.generic import TemplateView

app_name = "planner"

urlpatterns = [
    path(
        "start/",
        TemplateView.as_view(template_name="planner/plan_start.html"),
        name="plan_start",
    ),
    # (추가적인 템플릿 URL이 있으면 여기에 계속 작성)
]
