from rest_framework import serializers
from onboard.models import ChecklistItem
from onboard.models import UserChecklist


class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['req_id', 'feature', 'message', 'fallback_message']
        
class UserChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChecklist
        fields = ['id', 'user', 'country', 'req_id', 'is_checked']
        read_only_fields = ['user']
