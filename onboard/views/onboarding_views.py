from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework import serializers
from drf_spectacular.utils import extend_schema
from django.shortcuts import render


from ..models import Country, InterestItem, UserOnboarding, InterestCategory
from ..serializers import CountrySerializer, InterestItemSerializer

# --- Serializers ---
class SaveOnboardingSerializer(serializers.Serializer):
    country = serializers.IntegerField()
    items = serializers.ListField(child=serializers.IntegerField(), required=False)

class LoadOnboardingSerializer(serializers.Serializer):
    countries = serializers.ListField(child=serializers.IntegerField())
    items = serializers.ListField(child=serializers.IntegerField())

class OnboardingOptionsSerializer(serializers.Serializer):
    countries = serializers.ListSerializer(child=serializers.DictField())
    categories = serializers.ListSerializer(child=serializers.DictField())

# --- Views ---

@extend_schema(responses=LoadOnboardingSerializer)
class LoadOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        onboarding = get_object_or_404(UserOnboarding, user=request.user)
        country_ids = onboarding.countries.values_list('id', flat=True)
        item_ids = onboarding.interest_items.values_list('id', flat=True)
        return Response({
            'countries': list(country_ids),
            'items': list(item_ids),
        })

@extend_schema(responses=OnboardingOptionsSerializer)
class OnboardingOptionsView(APIView):
    def get(self, request):
        countries = Country.objects.all().values('id', 'name', 'code')
        categories = InterestCategory.objects.prefetch_related('items').all()

        category_list = []
        for category in categories:
            items = category.items.all().values('id', 'name')
            category_list.append({
                'id': category.id,
                'name': category.name,
                'items': list(items)
            })

        return Response({
            'countries': list(countries),
            'categories': category_list,
        })

@extend_schema(request=SaveOnboardingSerializer, responses={"200": serializers.JSONField()})
class SaveOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        country_id = data.get('country')
        item_ids = data.get('items', [])

        country = get_object_or_404(Country, id=country_id)
        onboarding, _ = UserOnboarding.objects.get_or_create(user=request.user)
        onboarding.countries.set([country])
        onboarding.interest_items.set(item_ids)
        return Response({"status": "saved"})

# 템플릿 기반 메인 뷰
class OnboardMainView(TemplateView):
    template_name = 'onboard/onboard_main.html'

# 국가/관심항목 리스트 API
class CountryListView(ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class InterestItemListView(ListAPIView):
    queryset = InterestItem.objects.all()
    serializer_class = InterestItemSerializer

# --- 템플릿용 화면 렌더링 함수 추가 ---


def select_country(request):
    return render(request, "onboard/select_country.html")

def checklist(request):
    return render(request, "onboard/checklist.html")

def extra_info(request):
    return render(request, "onboard/extra_info.html")

