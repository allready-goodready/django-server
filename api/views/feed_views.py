from feed.models import Feed, FeedImage
from api.serializers.feed_serializers import FeedSerializer
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.renderers import JSONRenderer

# 피드 등록 API
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


# 커스텀 페이지네이션 
class FeedPagination(PageNumberPagination) : 
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 120


# 피드 목록 API
class FeedListView(ListAPIView) : 
    queryset = Feed.objects.all().order_by('-created_at')   # 최신순
    serializer_class = FeedSerializer
    pagination_class = FeedPagination
    
    # 정렬, 검색
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at']    # , 'like_count' 추가 예정
    ordering = ['-created_at']  # 기본 정렬 기준
    search_fields = ['caption', 'place']    # , 'user__username' 추가 예정
    renderer_classes = [JSONRenderer]