from django.urls import path
from api.views.feed_views import FeedCreateView

app_name = 'api_feed'

urlpatterns = [
    path('feed/create/', FeedCreateView.as_view(), name='feed-create-api'),
]