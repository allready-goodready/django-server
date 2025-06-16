from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signin/', views.SignInView.as_view(), name='signin'),
    path('signout/', views.SignOutView.as_view(), name='signout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),

    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update_profile'),
    
    path('kakao/login/', views.KakaoLoginView.as_view(), name='kakao_login'),
    path('kakao/login/callback/', views.KakaoCallbackView.as_view(), name='kakao_callback'),
    path('google/login/', views.GoogleLoginView.as_view(), name='google_login'),
    path('google/login/callback/', views.GoogleCallbackView.as_view(), name='google_callback'),
    path('send-verification-email/', views.EmailVerificationView.as_view(), name='send_verification_email'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
]