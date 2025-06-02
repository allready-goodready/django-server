from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import TravelPlan, Location, FlightOption


### 1) Draft TravelPlan 생성 함수 ###
def create_travelplan_draft(user, validated_data):
    """
    - user: request.user
    - validated_data: TravelPlanDraftSerializer.validated_data
    """
    plan = TravelPlan.objects.create(
        user=user,
        title=validated_data["title"],
        start_date=validated_data["start_date"],
        end_date=validated_data["end_date"],
        budget_limit=validated_data["budget_limit"],
        status="draft",
    )
    return plan


### 2) Draft TravelPlan에 Location 추가 함수 ###
def add_location_to_plan(plan_id, location_data):
    """
    - plan_id: TravelPlan.pk (UUID)
    - location_data: LocationCreateSerializer.validated_data (dict)
    반드시 status='draft'인 Plan만 허용.
    """
    try:
        plan = TravelPlan.objects.get(id=plan_id, status="draft")
    except ObjectDoesNotExist:
        raise ValueError("유효한 draft 상태의 TravelPlan이 없습니다.")

    loc = Location.objects.create(
        plan=plan,
        name=location_data["name"],
        address=location_data["address"],
        lat=location_data["lat"],
        lng=location_data["lng"],
        type=location_data["type"],
    )
    return loc


### 3) Draft TravelPlan에 FlightOption 추가 함수 ###
def add_flightoption_to_plan(plan_id, flight_data):
    """
    - plan_id: TravelPlan.pk (UUID)
    - flight_data: FlightOptionCreateSerializer.validated_data (dict)
    반드시 status='draft'인 Plan만 허용.
    """
    try:
        plan = TravelPlan.objects.get(id=plan_id, status="draft")
    except ObjectDoesNotExist:
        raise ValueError("유효한 draft 상태의 TravelPlan이 없습니다.")

    # (필요 시) 외부 API로 공항 코드 검증/탐색 로직을 여기에 넣을 수 있음.
    # ex) departure_airport, arrival_airport가 실제 존재하는 공항인지 확인 등

    fo = FlightOption.objects.create(
        plan=plan,
        departure_airport=flight_data["departure_airport"],
        arrival_airport=flight_data["arrival_airport"],
        departure_datetime=flight_data["departure_datetime"],
        arrival_datetime=flight_data["arrival_datetime"],
        price=flight_data["price"],
    )
    return fo


### 4) Draft TravelPlan을 Confirm(최종 확정) 처리 함수 ###
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
