from django.shortcuts import render

# Create your views here.

# FD-01 : 피드 등록 화면
def feed_create(request) : 
    return render(request, "feed/feed_create.html")


# FD-01 : 피드 등록 화면 띄우기 위한 피드 목록 화면
def feed_list(request) : 
    return render(request, "feed/feed_list.html")
