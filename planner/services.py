from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import TravelPlan


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
