from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator
from feed.models import Feed

# Create your views here.

# FD-01 : 피드 등록 화면
def feed_create(request) : 
    return render(request, "feed/feed_create.html", { 
        "google_api_key": settings.GOOGLE_API_KEY,
        # "username": request.user.username,
        # "profile_image_url": request.user.profile.image.url,
    })


# FD-04 : 피드 목록 화면
def feed_list(request) : 
    feed_all = Feed.objects.all().order_by('-created_at')
    paginator = Paginator(feed_all, 12)  # 한 페이지당 12개
    page = request.GET.get('page')
    feeds = paginator.get_page(page)
    return render(request, "feed/feed_list.html", { 'feeds': feeds })
