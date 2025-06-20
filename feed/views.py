from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator
from feed.models import Bookmark, Feed, Like


from feed.models import Feed, FeedImage
from feed.serializers import FeedSerializer
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Count

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
    queryset = Feed.objects.annotate(like_count=Count("likes")).order_by('-created_at')   # 최신순
    serializer_class = FeedSerializer
    pagination_class = FeedPagination
    
    # 정렬, 검색
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'like_count']
    ordering = ['-created_at']  # 기본 정렬 기준
    search_fields = ['caption', 'place', 'user__username']
    renderer_classes = [JSONRenderer]

# FD-08 : 피드 상세 api
class FeedDetailView(RetrieveAPIView) :
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 허용

    lookup_field = 'id'     # 모델에서 조회 기준이 되는 필드
    lookup_url_kwarg = 'feed_id'    # url에서 받아올 변수명과 맞춰줌
    renderer_classes = [JSONRenderer]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# FD-06 : 피드 좋아요 api
class FeedLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, feed_id) : 
        try:
            feed = Feed.objects.get(pk=feed_id)
        except Feed.DoesNotExist:
            return Response({"error": "피드가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        like_obj = Like.objects.filter(user=user, feed=feed).first()

        if like_obj:
            like_obj.delete()
            liked = False
        else:
            Like.objects.create(user=user, feed=feed)
            liked = True

        return Response({
            "is_liked": liked,
            "like_count": feed.likes.count()
        }, status=status.HTTP_200_OK)
    

# FD-07 : 피드 북마크 api
class FeedBookmarkAPIView(APIView) : 
    permission_classes = [IsAuthenticated]

    def post(self, request, feed_id) : 
        try:
            feed = Feed.objects.get(pk=feed_id)
        except Feed.DoesNotExist:
            return Response({"error": "피드가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        bookmark_obj = Bookmark.objects.filter(user=user, feed=feed).first()

        if bookmark_obj:
            bookmark_obj.delete()
            bookmarked = False
        else:
            Bookmark.objects.create(user=user, feed=feed)
            bookmarked = True

        return Response({
            "is_bookmarked": bookmarked,
        }, status=status.HTTP_200_OK)


# FD-09 : 내가 작성한 피드 목록 api
class MyFeedListAPIView(ListAPIView) : 
    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Feed.objects.filter(user=self.request.user).order_by('-created_at')
    

# FD-10 : 내가 북마크한 피드 목록 api
class MyBookmarkListView(ListAPIView):
    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Feed.objects.filter(bookmarks__user=self.request.user).order_by('-created_at')