# onboard/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Country, InterestItem, UserOnboarding
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated


User = get_user_model()

class SaveOnboardingView(APIView):
    def post(self, request):
        user = request.user
        countries = request.data.get('countries', [])
        interests = request.data.get('interests', [])

        onboarding, _ = UserOnboarding.objects.get_or_create(user=user)
        onboarding.countries.set(countries)
        onboarding.interest_items.set(interests)
        onboarding.save()

        return Response({"message": "온보딩 정보 저장 완료!"}, status=status.HTTP_200_OK)

class LoadOnboardingView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        try:
            onboarding = UserOnboarding.objects.get(user=user)
            data = {
                "countries": [c.id for c in onboarding.countries.all()],
                "interests": [i.id for i in onboarding.interest_items.all()]
            }
            return Response(data)
        except UserOnboarding.DoesNotExist:
            return Response({"message": "아직 온보딩 정보 없음"}, status=204)

class OnboardMainView(TemplateView):
    template_name = 'onboard/onboard_main.html'
