from django.urls import path
from api.views.feed_views import FeedCreateView, FeedListView

app_name = 'api'

urlpatterns = [
    path('feed/create/', FeedCreateView.as_view(), name='feed-create-api'),
    path('feeds/', FeedListView.as_view(), name='feed-list-api'),
]

