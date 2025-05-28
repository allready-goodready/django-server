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
        여행 시작일이 종료일보다 늦을 수 없고,
        budget_limit은 음수일 수 없습니다.
        """
        start = attrs.get("start_date") or getattr(self.instance, "start_date", None)
        end = attrs.get("end_date")   or getattr(self.instance, "end_date", None)
        if start and end and start > end:
            raise serializers.ValidationError("여행 시작일은 종료일 이전이거나 같아야 합니다.")
        
        budget = attrs.get("budget_limit")
        if budget is not None and budget < 0:
            raise serializers.ValidationError("예산은 0원 이상 이어야 합니다.")
        
        return attrs
