from django.db import models
from django.conf import settings

# Create your models here.

class Feed(models.Model) : 
    # User 모델이 아직 정의되지 않아 user 필드는 임시로 주석 처리했습니다.
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    caption = models.CharField(max_length=200, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # 장소 정보
    place = models.CharField(max_length=100)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    def __str__(self) : 
        # return f"{self.user.username}의 피드"
        return f"피드({self.id}) - {self.caption[:10]}..."

class FeedImage(models.Model) : 
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='feeds/', blank=False, null=False)
    order = models.PositiveIntegerField(default=0)  # 이미지 순서

    def __str__(self) : 
        return f"피드({self.feed.id}) 의 이미지"
    
