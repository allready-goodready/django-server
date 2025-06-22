# onboard/models/checklist_models.py

from django.db import models

class ChecklistCategory(models.Model):
    name = models.CharField(max_length=50)  # ex: "출국 전 준비", "여행 꿀팁"

    def __str__(self):
        return self.name

class ChecklistItem(models.Model):
    name = models.CharField(max_length=255, default="이름없음")
    category = models.ForeignKey(ChecklistCategory, on_delete=models.CASCADE, related_name='items')
    req_id = models.CharField(max_length=20, unique=True)
    feature = models.CharField(max_length=100)  # 기능명
    description = models.TextField()  # 설명
    input_condition = models.CharField(max_length=100)  # 입력 조건
    output_description = models.TextField()  # 출력 설명
    fallback_message = models.TextField()  # 예외처리 메시지
    note = models.TextField(blank=True, null=True)  # 비고
    country_code = models.CharField(max_length=5, blank=True, null=True)
    message = models.TextField(blank=True, null=True)  # 실제 안내 메시지
    detail = models.TextField(blank=True, null=True)  # 상세 설명

    def __str__(self):
        return f"[{self.req_id}] {self.feature}"
