from django.utils.timezone import localdate
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Location, TravelPlan
from .services import upsert_location

User = get_user_model()


class TravelPlanDraftSerializer(serializers.ModelSerializer):
    """
    1) 클라이언트가 여행 일정·예산을 입력하면,
    2) status='draft'로 TravelPlan 인스턴스를 생성하기 위해 사용하는 Serializer입니다.

    - id, created_at, updated_at 필드는 읽기 전용(read_only).
    - user는 요청한 유저(request.user)를 자동으로 할당.
    - status는 항상 'draft'로 세팅(사용자가 별도로 입력하지 않음).
    """

    id = serializers.UUIDField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    status = serializers.CharField(
        read_only=True
    )  # 항상 'draft'로 생성되므로 read_only
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
            "status",
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
        # 1) 필수 입력 검증 (create/update 상관 없이)
        if attrs.get("start_date") is None:
            raise serializers.ValidationError(
                {"start_date": "여행 시작일을 입력해주세요."}
            )
        if attrs.get("end_date") is None:
            raise serializers.ValidationError(
                {"end_date": "여행 종료일을 입력해주세요."}
            )

        # 2) 값 가져오기
        start = attrs.get("start_date")
        end = attrs.get("end_date")

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

    def create(self, validated_data):
        """
        TravelPlanDraft 생성 시, status='draft'로 강제 설정하여 저장합니다.
        """
        # user 필드는 HiddenField로 이미 들어온 상태
        # validated_data에는 title, start_date, end_date, budget_limit, user가 존재
        plan = TravelPlan.objects.create(
            user=validated_data["user"],
            title=validated_data.get("title", ""),
            start_date=validated_data["start_date"],
            end_date=validated_data["end_date"],
            budget_limit=validated_data["budget_limit"],
            status="draft",
        )
        return plan


class TravelPlanUpdateSerializer(serializers.ModelSerializer):
    """
    - Draft 상태 여행 계획을 수정할 때 사용합니다.
    - 기존 instance의 start_date/end_date는 이미 유효하게 저장된 값이므로,
      attrs에서 값이 없으면 instance의 값을 그대로 사용합니다.
    - 새로운 값이 들어올 때만 '오늘 이전인지', '시작 ≤ 종료인지', '예산 ≥ 0인지'를 재검증합니다.
    - status='confirmed' 상태인 경우 수정할 수 없도록 막습니다.
    """

    id = serializers.UUIDField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.CharField(read_only=True)

    class Meta:
        model = TravelPlan
        fields = (
            "id",
            "user",
            "title",
            "start_date",
            "end_date",
            "budget_limit",
            "status",
        )

    def validate(self, attrs):
        instance: TravelPlan = getattr(self, "instance", None)

        # 1) 이미 'confirmed' 상태라면 수정 불가
        if instance and instance.status == "confirmed":
            raise serializers.ValidationError(
                {"detail": "이미 확정된 여행 계획은 수정할 수 없습니다."}
            )

        # 2) 기존 값과 새로 들어온 값을 조합
        #    - 클라이언트가 start_date를 보내지 않으면 instance.start_date
        #    - 보내면 attrs['start_date']
        start = attrs.get("start_date") or instance.start_date
        end = attrs.get("end_date") or instance.end_date

        # 3) ‘새로 들어온 값’만 검사하는 게 아니라, 최종 start/end 조합이 유효한지 검증
        if start < localdate():
            raise serializers.ValidationError(
                {"start_date": "여행 시작일은 오늘 또는 이후의 날짜여야 합니다."}
            )
        if start > end:
            raise serializers.ValidationError(
                {"end_date": "여행 종료일은 시작일 이후이거나 같아야 합니다."}
            )

        # 4) budget_limit이 들어왔을 때만 ≥ 0인지 확인
        if "budget_limit" in attrs:
            budget = attrs["budget_limit"]
            if budget < 0:
                raise serializers.ValidationError(
                    {"budget_limit": "예산은 0원 이상이어야 합니다."}
                )

        return attrs


class TravelPlanConfirmSerializer(serializers.Serializer):
    """
    최종 확정(Confirm) 단계에서 사용하는 Serializer.
    - 별도의 필드는 필요 없으므로, 바디 없이 호출해도 통과하도록만 만듭니다.
    """

    def validate(self, attrs):
        return attrs


class LocationModelSerializer(serializers.ModelSerializer):
    """
    - plan: write_only, 뷰에서 save(plan=...) 형태로 주입
    - type: 뷰에서 자동 주입하므로 required=False
    - place_id, name, address, lat, lng: 클라이언트에서 전달
    - create(): upsert_location 호출
    - update(): type/plan 변경 금지, 나머지 필드만 덮어씀
    """

    plan = serializers.PrimaryKeyRelatedField(
        queryset=TravelPlan.objects.all(), write_only=True, required=False
    )
    type = serializers.ChoiceField(
        choices=Location.TYPE_CHOICES,
        required=False,  # 뷰에서 자동 주입하므로 클라이언트 입력 없이도 무방
    )

    class Meta:
        model = Location
        fields = (
            "id",
            "plan",  # write_only
            "type",  # 뷰에서 주입
            "place_id",
            "name",
            "address",
            "lat",
            "lng",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        """
        - create 시: 뷰에서 'type'을 주입하므로 attrs.get("type")이 존재
        - update 시: instance가 생성된 상태이므로 attrs.get("type")은 없어도 됨
        - 위경도 범위(-90 ≤ lat ≤ 90, -180 ≤ lng ≤ 180) 체크
        """
        # 1) type 검증:
        loc_type = attrs.get("type", None)
        if not self.instance:
            # create 시: 반드시 type이 있어야 함
            if loc_type not in ["origin", "destination"]:
                raise serializers.ValidationError(
                    {"type": "type 필드는 'origin' 또는 'destination'이어야 합니다."}
                )
        else:
            # update 시: attrs에 type이 있으면 기존 instance.type과 비교
            if loc_type is not None and loc_type != self.instance.type:
                raise serializers.ValidationError(
                    {"type": "이미 저장된 Location의 type은 변경할 수 없습니다."}
                )

        # 2) 위도(lat) 필수 및 범위 검사
        lat = attrs.get("lat", getattr(self.instance, "lat", None))
        if lat is None:
            raise serializers.ValidationError({"lat": "위도(lat) 값이 필요합니다."})
        if not (-90.0 <= lat <= 90.0):
            raise serializers.ValidationError(
                {"lat": "위도(lat)는 -90.0 이상, 90.0 이하의 값이어야 합니다."}
            )

        # 3) 경도(lng) 필수 및 범위 검사
        lng = attrs.get("lng", getattr(self.instance, "lng", None))
        if lng is None:
            raise serializers.ValidationError({"lng": "경도(lng) 값이 필요합니다."})
        if not (-180.0 <= lng <= 180.0):
            raise serializers.ValidationError(
                {"lng": "경도(lng)는 -180.0 이상, 180.0 이하의 값이어야 합니다."}
            )

        # 4) place_id, name, address 검사:
        #    create 시 반드시 있어야 함
        if not self.instance:
            required_fields = ["name", "address"]
            missing = [f for f in required_fields if attrs.get(f) is None]
            if missing:
                raise serializers.ValidationError(
                    {field: "이 필드는 반드시 필요합니다." for field in missing}
                )

        return attrs

    def create(self, validated_data):
        """
        - validated_data: {'plan': TravelPlan 인스턴스, 'type': str, 'place_id': str, 'name': str, 'address': str, 'lat': float, 'lng': float}
        - upsert_location을 호출하여 존재하면 수정, 없으면 생성
        """
        plan = validated_data.pop("plan")
        user = self.context["request"].user
        location, created = upsert_location(
            user=user, plan_id=plan.id, validated_data=validated_data
        )
        return location

    def update(self, instance, validated_data):
        """
        - instance: 기존 Location 인스턴스
        - validated_data에는 'type'이나 'plan'이 있으면 무시, 나머지 필드만 덮어쓰기
        """
        validated_data.pop("type", None)
        validated_data.pop("plan", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
