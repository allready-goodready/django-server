from django.db import models

from .models import Feed, FeedImage

# Create your models here.
@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'place', 'created_at') # user 빠져있음
    search_fields = ('caption', 'place')

@admin.register(FeedImage)
class FeedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'feed', 'order')