from rest_framework import generics
from feed.models import Feed, FeedImage
from api.serializers.feed_serializers import FeedSerializer
from rest_framework.generics import CreateAPIView

class FeedCreateView(CreateAPIView) : 
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer

    def perform_create(self, serializer) : 
        # feed = serializer.save(user=self.request.user)    # user 필드가 아직 정의되지 않아서 주석 처리했습니다.
        feed = serializer.save()

        # 이미지도 함께 저장
        images = self.request.FILES.getlist('images')
        for idx, img in enumerate(images) : 
            FeedImage.objects.create(feed=feed, image=img, order=idx+1)