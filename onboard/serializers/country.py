from rest_framework import serializers
from onboard.models import Country
from onboard.models import UserChecklist

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code']

class CountryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'code', 'currency_code']

class UserChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChecklist
        fields = ['id', 'user', 'country', 'req_id', 'is_checked']
        read_only_fields = ['user']