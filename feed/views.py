from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator
from feed.models import Feed


from feed.models import Feed, FeedImage
from feed.serializers import FeedSerializer
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated

# Create your views here.

# FD-01 : 피드 등록 화면
def feed_create(request) : 
    return render(request, "feed/feed_create.html", { 
        "google_api_key": settings.GOOGLE_API_KEY,
        # "username": request.user.username,
        # "profile_image_url": request.user.profile.image.url,
    })

# FD-02 : 피드 등록 api
class FeedCreateView(CreateAPIView) : 
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 허용

    queryset = Feed.objects.all()
    serializer_class = FeedSerializer

    def perform_create(self, serializer) : 
        feed = serializer.save(user=self.request.user)    # user 필드가 아직 정의되지 않아서 주석 처리했습니다.
        # feed = serializer.save()

        # 이미지도 함께 저장
        images = self.request.FILES.getlist('images')
        for idx, img in enumerate(images) : 
            FeedImage.objects.create(feed=feed, image=img, order=idx+1)

        return Response(serializer.data, status=201)


# FD-03 : 피드 목록 화면
def feed_list(request) : 
    feed_all = Feed.objects.all().order_by('-created_at')
    paginator = Paginator(feed_all, 12)  # 한 페이지당 12개
    page = request.GET.get('page')
    feeds = paginator.get_page(page)
    return render(request, "feed/feed_list.html", { 'feeds': feeds })


# 커스텀 페이지네이션 
class FeedPagination(PageNumberPagination) : 
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 120

# FD-04 : 피드 목록 api
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