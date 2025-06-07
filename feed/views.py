from django.shortcuts import render
from django.conf import settings

# Create your views here.

# FD-01 : 피드 등록 화면
def feed_create(request) : 
    return render(request, "feed/feed_create.html", { 
        "google_api_key": settings.GOOGLE_API_KEY,
        # "username": request.user.username,
        # "profile_image_url": request.user.profile.image.url,
    })


# FD-01 : 피드 등록 화면 띄우기 위한 피드 목록 화면
def feed_list(request) : 
    return render(request, "feed/feed_list.html", { "google_api_key": settings.GOOGLE_API_KEY })
