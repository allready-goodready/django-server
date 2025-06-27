from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from .models import TravelPlan, Location


def confirm_travelplan(plan_id):
    """
    1) plan = TravelPlan(id=plan_id, status='draft') 조회
    2) 필수 종속 객체(Location ≥1개, FlightOption ≥1개 등) 유무 확인
    3) 트랜잭션으로 상태 변경 (status='confirmed')
    """
    try:
        plan = TravelPlan.objects.get(id=plan_id, status="draft")
    except ObjectDoesNotExist:
        raise ValueError("확정 가능한 draft 상태의 여정이 없습니다.")

    # 필수 연결 객체 개수 검증 (본인 요구사항에 따라 수정 가능)
    if plan.locations.count() < 2:
        raise ValueError("최소 2개 이상의 Location이 필요합니다.")
    if plan.flights.count() < 2:
        raise ValueError("최소 2개 이상의 FlightOption이 필요합니다.")

    # 트랜잭션으로 상태 변경
    with transaction.atomic():
        plan.status = "confirmed"
        plan.save()
    return plan


def upsert_location(user, plan_id, validated_data):
    """
    - user: 요청을 보낸 사용자 (request.user)
    - plan_id: URL 경로로 받아온 TravelPlan의 pk
    - validated_data: {'type', 'place_id', 'name', 'address', 'lat', 'lng'} 형태로 들어옴

    1) plan이 user 소유인지 검증(get_object_or_404)
    2) plan + type 조합의 Location이 이미 존재하면 update,
       존재하지 않으면 create
    3) 생성 또는 수정된 Location 인스턴스와 생성 여부(created: bool) 반환
    """
    # 1) TravelPlan 조회 및 소유권 체크
    plan = get_object_or_404(TravelPlan, pk=plan_id, user=user)

    loc_type = validated_data.get("type")
    place_id = validated_data.get("place_id")
    name = validated_data.get("name")
    address = validated_data.get("address")
    lat = validated_data.get("lat")
    lng = validated_data.get("lng")

    # 2) 이미 같은 plan & type의 Location이 있는지 조회
    try:
        location = Location.objects.get(plan=plan, type=loc_type)
        # 존재하면 필드만 덮어쓰기
        location.place_id = place_id
        location.name = name
        location.address = address
        location.lat = lat
        location.lng = lng
        location.save()
        created = False
    except Location.DoesNotExist:
        # 없으면 새로 생성
        location = Location.objects.create(
            plan=plan,
            type=loc_type,
            place_id=place_id,
            name=name,
            address=address,
            lat=lat,
            lng=lng,
        )
        created = True

    return location, created
