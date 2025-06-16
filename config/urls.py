from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from accounts import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.BaseView.as_view(), name='base'),  # 메인 페이지
    path('accounts/', include('accounts.urls')), # accounts
    path('accounts/', include('allauth.urls')), # allauth URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
