from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from planner.models import TravelPlan

# drf-spectacular 문서화 데코레이터
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .services import (
    get_nearest_airport,
    search_flight_offers,
    prioritize_offers,
    get_airlines_info,
    book_flight,
)
from .models import FlightSelection


@extend_schema(
    tags=["Flight"],
    summary="항공편 검색",
    description="여행 계획을 기반으로 항공편을 검색합니다.",
    parameters=[
        OpenApiParameter(
            name="plan_id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description="여행 계획 ID",
            required=True,
        ),
        OpenApiParameter(
            name="adults",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="성인 승객 수 (기본값: 1)",
        ),
        OpenApiParameter(
            name="earliest_dep",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="최소 출발 시간 (HH:MM 형식)",
        ),
        OpenApiParameter(
            name="latest_arr",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="최대 도착 시간 (HH:MM 형식)",
        ),
    ],
)
class FlightSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_id = request.query_params.get("plan_id")
        adults = request.query_params.get("adults", 1)
        earliest_dep = request.query_params.get("earliest_dep")
        latest_arr = request.query_params.get("latest_arr")

        plan = get_object_or_404(TravelPlan, id=plan_id, user=request.user)
        origin_loc = plan.locations.filter(type="origin").first()
        dest_loc = plan.locations.filter(type="destination").first()
        origin_airport = get_nearest_airport(origin_loc.lat, origin_loc.lng)
        dest_airport = get_nearest_airport(dest_loc.lat, dest_loc.lng)
        if not origin_airport or not dest_airport:
            return Response({"error": "Airport info missing."}, status=400)

        offers = search_flight_offers(
            origin_airport["iata"],
            dest_airport["iata"],
            plan.start_date.isoformat(),
            plan.end_date.isoformat(),
            adults=int(adults),
        )

        # 1) 유니크 항공사 코드 추출
        codes = set()
        for o in offers:
            # validatingAirlineCodes 우선, 없으면 첫 segment 의 carrierCode
            code = (
                o.get("validatingAirlineCodes")
                or [o["itineraries"][0]["segments"][0]["carrierCode"]]
            )[0]
            codes.add(code)

        # 2) Reference Data API 로 항공사명 조회
        airline_info = get_airlines_info(list(codes))

        # 3) offers 에 outboundAirlineName, returnAirlineName 필드 주입
        for o in offers:
            # 출국편 항공사 코드: validatingAirlineCodes 우선, 없으면 첫 세그먼트의 carrierCode
            out_code = (
                o.get("validatingAirlineCodes")
                or [o["itineraries"][0]["segments"][0]["carrierCode"]]
            )[0]
            # 귀국편 항공사 코드: return itinerary 첫 세그먼트의 carrierCode
            in_code = o["itineraries"][1]["segments"][0]["carrierCode"]

            o["outboundAirlineName"] = airline_info.get(out_code, {}).get(
                "commonName", out_code
            )
            o["returnAirlineName"] = airline_info.get(in_code, {}).get(
                "commonName", in_code
            )

        # 시간 필터
        if earliest_dep:
            offers = [
                o
                for o in offers
                if o["itineraries"][0]["segments"][0]["departure"]["at"].split("T")[1]
                >= earliest_dep
            ]
        if latest_arr:
            offers = [
                o
                for o in offers
                if o["itineraries"][1]["segments"][-1]["arrival"]["at"].split("T")[1]
                <= latest_arr
            ]

        # 기본값 선정
        default_offer = prioritize_offers(offers)[0] if offers else None

        # 캐싱 로직
        FlightSelection.objects.update_or_create(
            plan=plan,
            defaults={
                "departure_iata": origin_airport["iata"],
                "arrival_iata": dest_airport["iata"],
                "offers_data": offers,
            },
        )

        return Response({"offers": offers, "default_offer": default_offer})


@extend_schema(
    tags=["Flight"],
    summary="항공편 후보 조회",
    description="이전에 검색한 항공편 후보들을 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="plan_id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description="여행 계획 ID",
            required=True,
        ),
    ],
)
class FlightCandidatesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_id = request.query_params.get("plan_id")
        plan = get_object_or_404(TravelPlan, id=plan_id, user=request.user)
        fs = get_object_or_404(FlightSelection, plan=plan)
        return Response(
            {
                "offers": fs.offers_data or [],
                "selected_offer": fs.selected_offer_snapshot,
            }
        )


@extend_schema(
    tags=["Flight"],
    summary="항공편 선택",
    description="검색된 항공편 중 하나를 선택합니다.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "여행 계획 ID",
                },
                "offer_id": {"type": "string", "description": "선택할 항공편 제안 ID"},
                "offer_snapshot": {
                    "type": "object",
                    "description": "선택한 항공편의 상세 정보",
                },
            },
            "required": ["plan_id", "offer_id", "offer_snapshot"],
        }
    },
)
class FlightSelectAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("plan_id")
        offer_id = request.data.get("offer_id")
        offer_snapshot = request.data.get("offer_snapshot")

        plan = get_object_or_404(TravelPlan, id=plan_id, user=request.user)
        flight_sel, _ = FlightSelection.objects.update_or_create(
            plan=plan,
            defaults={
                "selected_offer_id": offer_id,
                "selected_offer_snapshot": offer_snapshot,
            },
        )
        return Response({"success": True}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Flight"],
    summary="항공편 예약",
    description="선택한 항공편을 실제로 예약합니다.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "여행 계획 ID",
                },
            },
            "required": ["plan_id"],
        }
    },
    responses={
        200: {"description": "예약 성공"},
        400: {"description": "예약 실패 (사용자 정보 부족 등)"},
    },
)
class FlightBookAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan = get_object_or_404(
            TravelPlan, id=request.data.get("plan_id"), user=request.user
        )
        flight_sel = get_object_or_404(FlightSelection, plan=plan)

        offer_snapshot = flight_sel.selected_offer_snapshot

        # 실제 사용자 정보를 이용해 travelers 리스트 구성
        travelers = [
            {
                "id": "1",
                "dateOfBirth": request.user.profile.date_of_birth,
                "name": {
                    "firstName": request.user.first_name.upper(),
                    "lastName": request.user.last_name.upper(),
                },
                "gender": request.user.profile.gender.upper(),
                "contact": {
                    "emailAddress": request.user.email,
                    "phones": [
                        {
                            "deviceType": "MOBILE",
                            "countryCallingCode": "82",
                            "number": request.user.profile.phone_number,
                        }
                    ],
                },
                "documents": [
                    {
                        "documentType": "PASSPORT",
                        "birthPlace": request.user.profile.birth_place,
                        "issuanceLocation": request.user.profile.issuance_location,
                        "issuanceDate": request.user.profile.issuance_date,
                        "number": request.user.profile.passport_number,
                        "expiryDate": request.user.profile.passport_expiry_date,
                        "issuanceCountry": request.user.profile.nationality,
                        "validityCountry": request.user.profile.nationality,
                        "nationality": request.user.profile.nationality,
                        "holder": True,
                    }
                ],
            }
        ]

        remarks = {
            "general": [
                {
                    "subType": "GENERAL_MISCELLANEOUS",
                    "text": "ONLINE BOOKING FROM ALLREADY",
                }
            ]
        }
        ticketing_agreement = {"option": "DELAY_TO_CANCEL", "delay": "6D"}
        contacts = [
            {
                "addresseeName": {"firstName": "ALLREADY", "lastName": "SERVICE"},
                "companyName": "ALLREADY Inc.",
                "purpose": "STANDARD",
                "phones": [
                    {
                        "deviceType": "LANDLINE",
                        "countryCallingCode": "82",
                        "number": "02-1234-5678",
                    }
                ],
                "emailAddress": "support@allready.com",
                "address": {
                    "lines": ["123 Seoul St."],
                    "postalCode": "04524",
                    "cityName": "Seoul",
                    "countryCode": "KR",
                },
            }
        ]

        booking_data = book_flight(
            offer_snapshot,
            travelers,
            remarks=remarks,
            ticketing_agreement=ticketing_agreement,
            contacts=contacts,
        )

        flight_sel.booking_data = booking_data
        flight_sel.save(update_fields=["booking_data"])

        return Response({"booking_data": booking_data}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Flight"],
    summary="출발지 근처 공항 조회",
    description="여행 계획의 출발지 근처에 있는 공항 정보를 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="plan_id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description="여행 계획 ID",
            required=True,
        ),
    ],
)
class AirportNearOriginAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_id = request.query_params.get("plan_id")
        plan = get_object_or_404(TravelPlan, id=plan_id, user=request.user)
        origin_loc = plan.locations.filter(type="origin").first()
        if not origin_loc:
            return Response({"error": "Origin location not found."}, status=404)

        result = get_nearest_airport(origin_loc.lat, origin_loc.lng)
        if not result:
            return Response({"error": "Nearest airport not found."}, status=400)
        return Response(result)


@extend_schema(
    tags=["Flight"],
    summary="목적지 근처 공항 조회",
    description="여행 계획의 목적지 근처에 있는 공항 정보를 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="plan_id",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description="여행 계획 ID",
            required=True,
        ),
    ],
)
class AirportNearDestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_id = request.query_params.get("plan_id")
        plan = get_object_or_404(TravelPlan, id=plan_id, user=request.user)
        dest_loc = plan.locations.filter(type="destination").first()
        if not dest_loc:
            return Response({"error": "Destination location not found."}, status=404)

        result = get_nearest_airport(dest_loc.latitude, dest_loc.longitude)
        if not result:
            return Response({"error": "Nearest airport not found."}, status=400)
        return Response(result)
