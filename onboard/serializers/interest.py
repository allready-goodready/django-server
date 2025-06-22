from rest_framework import serializers
from onboard.models import InterestItem

class InterestItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestItem
        fields = ['id', 'name']
