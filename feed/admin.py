from django.contrib import admin
from .models import Feed, FeedImage


# Register your models here.


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("id", "caption", "place", "created_at")  # user 빠져있음
    search_fields = ("caption", "place")


@admin.register(FeedImage)
class FeedImageAdmin(admin.ModelAdmin):
    list_display = ("id", "feed", "order")
