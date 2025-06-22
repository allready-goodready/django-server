from rest_framework import serializers

class ExchangeRateSerializer(serializers.Serializer):
    base = serializers.CharField()
    target = serializers.CharField()
    rate = serializers.FloatField()
