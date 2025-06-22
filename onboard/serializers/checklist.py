from rest_framework import serializers
from onboard.models import ChecklistItem

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['req_id', 'feature', 'message', 'fallback_message']
