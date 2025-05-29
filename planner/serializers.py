from django.utils.timezone import localdate
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TravelPlan

User = get_user_model()


class TravelPlanSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = TravelPlan
        fields = (
            "id",
            "user",
            "title",
            "start_date",
            "end_date",
            "budget_limit",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        """
        - start_date, end_date는 반드시 입력되어야 합니다.
        - 여행 시작일이 오늘 이전일 수 없고,
        - 여행 시작일이 종료일보다 늦을 수 없으며,
        - budget_limit은 음수가 될 수 없습니다.
        """
        # 1) 필수 입력 검증 (create/update 구분 없이)
        if (
            attrs.get("start_date") is None
            and getattr(self.instance, "start_date", None) is None
        ):
            raise serializers.ValidationError(
                {"start_date": "여행 시작일을 입력해주세요."}
            )
        if (
            attrs.get("end_date") is None
            and getattr(self.instance, "end_date", None) is None
        ):
            raise serializers.ValidationError(
                {"end_date": "여행 종료일을 입력해주세요."}
            )

        # 2) 값 가져오기 (create 시 attrs, update 시 instance fallback)
        start = attrs.get("start_date") or getattr(self.instance, "start_date", None)
        end = attrs.get("end_date") or getattr(self.instance, "end_date", None)

        # 3) 오늘 이전일 수 없음
        if start < localdate():
            raise serializers.ValidationError(
                {"start_date": "여행 시작일은 오늘 또는 이후의 날짜여야 합니다."}
            )

        # 4) 시작일 ≤ 종료일
        if start > end:
            raise serializers.ValidationError(
                {"end_date": "여행 종료일은 시작일 이후이거나 같아야 합니다."}
            )

        # 5) 예산 음수 금지
        budget = attrs.get("budget_limit")
        if budget is not None and budget < 0:
            raise serializers.ValidationError(
                {"budget_limit": "예산은 0원 이상이어야 합니다."}
            )

        return attrs
