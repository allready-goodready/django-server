# onboard/models/user_checklist.py
from django.db import models
from django.conf import settings
from onboard.models import Country

class UserChecklist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    req_id = models.CharField(max_length=50)  # 예: 'VISA', 'PASSPORT'
    is_checked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'country', 'req_id')
