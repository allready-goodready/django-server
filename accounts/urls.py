from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('signin/', views.signin_view, name='signin'),
    path('signout/', views.signout_view, name='signout'),
    path('signup/', views.signup_view, name='signup'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    path('activities/', views.user_activities_view, name='activities'),
    
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('kakao/login/callback/', views.kakao_callback, name='kakao_callback'),
    path('google/login/', views.google_login, name='google_login'),
    path('google/login/callback/', views.google_callback, name='google_callback'),
    path('send-verification-email/', views.send_verification_email, name='send_verification_email'),
    path('verify-email/', views.verify_email, name='verify_email'),
]