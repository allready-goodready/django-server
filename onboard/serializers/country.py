from rest_framework import serializers
from onboard.models import Country

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']

class CountryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'code', 'currency_code']
