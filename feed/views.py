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

# drf-spectacular 문서화 데코레이터
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

# Create your views here.


# FD-01 : 피드 등록 화면
def feed_create(request):
    return render(
        request,
        "feed/feed_create.html",
        {
            "google_api_key": settings.GOOGLE_API_KEY,
            # "username": request.user.username,
            # "profile_image_url": request.user.profile.image.url,
        },
    )


# FD-02 : 피드 등록 api
@extend_schema(
    tags=["Feed"],
    summary="피드 등록",
    description="새로운 피드를 등록합니다. 인증된 사용자만 접근 가능합니다.",
    request=FeedSerializer,
    responses={201: FeedSerializer},
    examples=[
        OpenApiExample(
            "피드 등록 예시",
            value={
                "caption": "제주도 여행 중 맛있는 음식 발견!",
                "place": "제주도 서귀포시",
                "latitude": 33.2515,
                "longitude": 126.5603,
            },
            request_only=True,
        )
    ],
)
class FeedCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 허용

    queryset = Feed.objects.all()
    serializer_class = FeedSerializer

    def perform_create(self, serializer):
        feed = serializer.save(
            user=self.request.user
        )  # user 필드가 아직 정의되지 않아서 주석 처리했습니다.
        # feed = serializer.save()

        # 이미지도 함께 저장
        images = self.request.FILES.getlist("images")
        for idx, img in enumerate(images):
            FeedImage.objects.create(feed=feed, image=img, order=idx + 1)

        return Response(serializer.data, status=201)


# FD-03 : 피드 목록 화면
def feed_list(request):
    feed_all = Feed.objects.all().order_by("-created_at")
    paginator = Paginator(feed_all, 12)  # 한 페이지당 12개
    page = request.GET.get("page")
    feeds = paginator.get_page(page)
    return render(request, "feed/feed_list.html", {"feeds": feeds})


# 커스텀 페이지네이션
class FeedPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 120


# FD-04 : 피드 목록 api
@extend_schema(
    tags=["Feed"],
    summary="피드 목록 조회",
    description="모든 피드 목록을 페이지네이션과 함께 조회합니다. 정렬 및 검색 기능을 지원합니다.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="검색어 (caption, place, username으로 검색)",
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="정렬 기준 (created_at, like_count, -created_at, -like_count)",
        ),
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="페이지 번호",
        ),
    ],
    responses={200: FeedSerializer(many=True)},
)
class FeedListView(ListAPIView):
    queryset = Feed.objects.annotate(like_count=Count("likes")).order_by(
        "-created_at"
    )  # 최신순
    serializer_class = FeedSerializer
    pagination_class = FeedPagination

    # 정렬, 검색
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "like_count"]
    ordering = ["-created_at"]  # 기본 정렬 기준
    search_fields = ["caption", "place", "user__username"]
    renderer_classes = [JSONRenderer]


# FD-08 : 피드 상세 api
@extend_schema(
    tags=["Feed"],
    summary="피드 상세 조회",
    description="특정 피드의 상세 정보를 조회합니다. 현재 사용자의 좋아요, 북마크 상태도 함께 제공됩니다.",
    responses={200: FeedSerializer, 404: {"description": "피드가 존재하지 않습니다."}},
)
class FeedDetailView(RetrieveAPIView):
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 허용

    lookup_field = "id"  # 모델에서 조회 기준이 되는 필드
    lookup_url_kwarg = "feed_id"  # url에서 받아올 변수명과 맞춰줌
    renderer_classes = [JSONRenderer]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


# FD-06 : 피드 좋아요 api
@extend_schema(
    tags=["Feed"],
    summary="피드 좋아요/좋아요 취소",
    description="피드에 좋아요를 누르거나 취소합니다. 이미 좋아요가 있으면 취소, 없으면 좋아요를 추가합니다.",
    request=None,
    responses={
        200: {
            "type": "object",
            "properties": {
                "is_liked": {"type": "boolean", "description": "좋아요 상태"},
                "like_count": {"type": "integer", "description": "총 좋아요 수"},
            },
        },
        404: {"description": "피드가 존재하지 않습니다."},
    },
)
class FeedLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, feed_id):
        try:
            feed = Feed.objects.get(pk=feed_id)
        except Feed.DoesNotExist:
            return Response(
                {"error": "피드가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        user = request.user
        like_obj = Like.objects.filter(user=user, feed=feed).first()

        if like_obj:
            like_obj.delete()
            liked = False
        else:
            Like.objects.create(user=user, feed=feed)
            liked = True

        return Response(
            {"is_liked": liked, "like_count": feed.likes.count()},
            status=status.HTTP_200_OK,
        )


# FD-07 : 피드 북마크 api
@extend_schema(
    tags=["Feed"],
    summary="피드 북마크/북마크 취소",
    description="피드에 북마크를 추가하거나 취소합니다. 이미 북마크가 있으면 취소, 없으면 북마크를 추가합니다.",
    request=None,
    responses={
        200: {
            "type": "object",
            "properties": {
                "is_bookmarked": {"type": "boolean", "description": "북마크 상태"},
            },
        },
        404: {"description": "피드가 존재하지 않습니다."},
    },
)
class FeedBookmarkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, feed_id):
        try:
            feed = Feed.objects.get(pk=feed_id)
        except Feed.DoesNotExist:
            return Response(
                {"error": "피드가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        user = request.user
        bookmark_obj = Bookmark.objects.filter(user=user, feed=feed).first()

        if bookmark_obj:
            bookmark_obj.delete()
            bookmarked = False
        else:
            Bookmark.objects.create(user=user, feed=feed)
            bookmarked = True

        return Response(
            {
                "is_bookmarked": bookmarked,
            },
            status=status.HTTP_200_OK,
        )


# FD-09 : 내가 작성한 피드 목록 api
@extend_schema(
    tags=["Feed"],
    summary="내가 작성한 피드 목록",
    description="현재 사용자가 작성한 모든 피드 목록을 조회합니다.",
    responses={200: FeedSerializer(many=True)},
)
class MyFeedListAPIView(ListAPIView):
    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Feed.objects.filter(user=self.request.user).order_by("-created_at")


# FD-10 : 내가 북마크한 피드 목록 api
@extend_schema(
    tags=["Feed"],
    summary="내가 북마크한 피드 목록",
    description="현재 사용자가 북마크한 모든 피드 목록을 조회합니다.",
    responses={200: FeedSerializer(many=True)},
)
class MyBookmarkListView(ListAPIView):
    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Feed.objects.filter(bookmarks__user=self.request.user).order_by(
            "-created_at"
        )
