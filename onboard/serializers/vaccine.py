from rest_framework import serializers

class VaccineInfoSerializer(serializers.Serializer):
    country = serializers.CharField()
    required_vaccines = serializers.ListField(child=serializers.CharField())
