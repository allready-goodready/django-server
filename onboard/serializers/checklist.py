from rest_framework import serializers
from onboard.models import ChecklistItem
from onboard.models import UserChecklist
from rest_framework import serializers
from onboard.models.checklist_models import ChecklistItem

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['req_id', 'feature', 'message', 'fallback_message']
        
class UserChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChecklist
        fields = ['id', 'user', 'country', 'req_id', 'is_checked']
        read_only_fields = ['user']

class ChecklistDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['id', 'name', 'detail']
