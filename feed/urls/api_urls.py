# feed/urls/api_urls.py

from django.urls import path

from feed.views import FeedCreateView, FeedListView

app_name = 'feed-api'

urlpatterns = [
    path('create/', FeedCreateView.as_view(), name='feed-create-api'),  # /feed/api/create/
    path('feeds/', FeedListView.as_view(), name='feed-list-api'),       # /feed/api/feeds/
]

