# feed/urls/template_urls.py

from django.urls import path
from feed import views

app_name = "feed"

urlpatterns = [
    path("", views.feed_list, name="feed-list"),
]
