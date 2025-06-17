# feed/urls/api_urls.py

from django.urls import path

from feed.views import FeedCreateView, FeedDetailView, FeedListView

app_name = 'feed-api'

urlpatterns = [
    path('create/', FeedCreateView.as_view(), name='feed-create-api'),  # /feed/api/create/
    path('feeds/', FeedListView.as_view(), name='feed-list-api'),       # /feed/api/feeds/
    path('<int:feed_id>/', FeedDetailView.as_view(), name='feed-detail'),    # /feed/api/<int:feed_id>/
]

