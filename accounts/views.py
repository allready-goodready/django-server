# Django 기본
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import get_user_model

# 앱 모델 및 폼
from .models import Profile, EmailVerification
from .forms import ProfileUpdateForm, SignUpForm

# 소셜 로그인
from allauth.socialaccount.models import SocialAccount, SocialApp

# 기타 Django
from django.conf import settings
from django.views import View
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail

import requests

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

User = get_user_model()

class BaseView(View):
    def get(self, request):
        try:
            signup_completed = request.session.pop('signup_completed', False)
            context = {
                'signup_completed': signup_completed,
                'user': request.user
            }
            return render(request, 'base.html', context)
        except Exception as e:
            messages.error(request, '페이지 로딩 중 오류가 발생했습니다.')
            return render(request, 'base.html', {'user': request.user})

class EmailVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            if not email:
                return Response({
                    'status': 'error',
                    'message': '이메일을 입력해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=email).exists():
                return Response({
                    'status': 'error',
                    'message': '이미 사용 중인 이메일입니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            verification_code = EmailVerification.generate_verification_code()
            
            verification, created = EmailVerification.objects.update_or_create(
                email=email,
                defaults={
                    'verification_code': verification_code,
                    'is_verified': False
                }
            )
            
            subject = '이메일 인증 코드'
            message = f'회원가입을 위한 인증 코드는 {verification_code} 입니다.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            
            send_mail(subject, message, from_email, recipient_list)
            return Response({
                'status': 'success',
                'message': '인증 코드가 이메일로 전송되었습니다.'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': '이메일 전송 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            code = request.data.get('code')
            
            if not email or not code:
                return Response({
                    'status': 'error',
                    'message': '이메일과 인증 코드를 모두 입력해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                verification = EmailVerification.objects.get(
                    email=email,
                    verification_code=code
                )
                verification.is_verified = True
                verification.save()
                
                return Response({
                    'status': 'success',
                    'message': '이메일 인증이 완료되었습니다.'
                })
            except EmailVerification.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': '잘못된 인증 코드입니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': '이메일 인증 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'accounts/signup.html', {'form': form})
    
    def post(self, request):
        print("회원가입 시도:", request.POST)  # 디버깅용
        form = SignUpForm(request.POST)
        try:
            if form.is_valid():
                print("폼 유효성 검사 통과")  # 디버깅용
                if User.objects.filter(username=form.cleaned_data['username']).exists():
                    return JsonResponse({
                        'status': 'error',
                        'errors': {'username': ['이미 사용 중인 아이디입니다.']}
                    })
                
                email = form.cleaned_data['email']
                print(f"이메일 확인: {email}")  # 디버깅용
                
                try:
                    verification = EmailVerification.objects.get(
                        email=email,
                        is_verified=True
                    )
                    print(f"이메일 인증 상태: {verification.is_verified}")  # 디버깅용
                except EmailVerification.DoesNotExist:
                    print("이메일 인증 정보 없음")  # 디버깅용
                    return JsonResponse({
                        'status': 'error',
                        'errors': {'email': ['이메일 인증이 필요합니다.']}
                    })
                
                try:
                    print("사용자 생성 시도")  # 디버깅용
                    user = form.save()
                    print(f"사용자 생성 성공: {user.username}")  # 디버깅용
                    
                    # 사용자 인증 및 로그인
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    verification.delete()
                    
                    request.session['signup_completed'] = True
                    return JsonResponse({
                        'status': 'success',
                        'message': '회원가입이 완료되었습니다.',
                        'redirect_url': reverse('base')
                    })
                except Exception as e:
                    print(f"회원가입 상세 오류: {str(e)}")  # 디버깅용
                    import traceback
                    print(traceback.format_exc())  # 스택 트레이스 출력
                    return JsonResponse({
                        'status': 'error',
                        'message': f'회원가입 중 오류가 발생했습니다: {str(e)}'
                    })
            else:
                print("폼 유효성 검사 실패:", form.errors)  # 디버깅용
                errors = {}
                # non_field_errors 처리 (clean() 메서드의 오류)
                if form.non_field_errors():
                    errors['__all__'] = [str(error) for error in form.non_field_errors()]
                # 필드별 오류 처리
                for field, field_errors in form.errors.items():
                    if field == '__all__':
                        continue  # non_field_errors는 이미 처리했으므로 건너뜀
                    errors[field] = [str(error) for error in field_errors]
                
                return JsonResponse({
                    'status': 'error',
                    'errors': errors
                })
        except Exception as e:
            print(f"예상치 못한 오류: {str(e)}")  # 디버깅용
            import traceback
            print(traceback.format_exc())  # 스택 트레이스 출력
            return JsonResponse({
                'status': 'error',
                'message': f'회원가입 중 오류가 발생했습니다: {str(e)}'
            })

class SignInView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        form = AuthenticationForm(request, data=request.data)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return Response({
                'success': True,
                'message': '로그인되었습니다.'
            })
        else:
            return Response({
                'success': False,
                'message': '아이디 또는 비밀번호가 올바르지 않습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

class SignOutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, '로그아웃되었습니다.')
        return redirect('base')
        
    def post(self, request):
        logout(request)
        messages.success(request, '로그아웃되었습니다.')
        return redirect('base')

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        active_tab = request.GET.get('tab', 'feeds')
        
        context = {
            'user': user,
            'active_tab': active_tab,
        }
        
        return render(request, 'accounts/profile.html', context)

class UpdateProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProfileUpdateForm(instance=request.user.profile)
        return render(request, 'accounts/profile_update.html', {'form': form})
    
    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('accounts:profile')
        return render(request, 'accounts/profile_update.html', {'form': form})

class UserActivitiesView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/activities.html', {
            'message': '활동 내역 조회 기능은 추후 구현 예정'
        })

class KakaoLoginView(View):
    def get(self, request):
        # 기존 세션 로그아웃
        logout(request)
        
        # 카카오 로그아웃 처리
        client_id = settings.SOCIALACCOUNT_PROVIDERS['kakao']['APP']['client_id']
        redirect_uri = request.build_absolute_uri(reverse('accounts:kakao_callback'))
        
        # 카카오 로그인 URL로 리다이렉트
        return redirect(
            f'https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&prompt=login'
        )

class KakaoCallbackView(View):
    def get(self, request):
        try:
            code = request.GET.get('code')
            if not code:
                messages.error(request, '카카오 로그인에 실패했습니다.')
                return redirect('base')

            client_id = settings.SOCIALACCOUNT_PROVIDERS['kakao']['APP']['client_id']
            client_secret = settings.SOCIALACCOUNT_PROVIDERS['kakao']['APP']['secret']
            redirect_uri = request.build_absolute_uri(reverse('accounts:kakao_callback'))
            
            # 카카오 토큰 받기
            token_request = requests.post(
                'https://kauth.kakao.com/oauth/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': redirect_uri,
                    'code': code,
                }
            )
            token_json = token_request.json()
            if 'error' in token_json:
                messages.error(request, '카카오 인증에 실패했습니다.')
                return redirect('base')

            access_token = token_json.get('access_token')
            
            # 카카오 사용자 정보 받기
            profile_request = requests.get(
                'https://kapi.kakao.com/v2/user/me',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            profile_json = profile_request.json()
            if 'error' in profile_json:
                messages.error(request, '카카오 사용자 정보를 가져오는데 실패했습니다.')
                return redirect('base')

            kakao_account = profile_json.get('kakao_account')
            if not kakao_account:
                messages.error(request, '카카오 계정 정보를 가져오는데 실패했습니다.')
                return redirect('base')
            
            # 이메일 가져오기
            email = kakao_account.get('email')
            if not email:
                messages.error(request, '이메일 정보를 가져오는데 실패했습니다.')
                return redirect('base')
            
            try:
                # 기존 사용자 찾기
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # 새 사용자 생성
                username = f"kakao_{profile_json.get('id')}"
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=get_random_string(length=32)
                )
                messages.success(request, '카카오 계정으로 회원가입이 완료되었습니다.')
            
            # 로그인 (백엔드 명시)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, '카카오 로그인이 완료되었습니다.')
            return redirect('base')
            
        except Exception as e:
            messages.error(request, '카카오 로그인 중 오류가 발생했습니다.')
            return redirect('base')

class GoogleLoginView(View):
    def get(self, request):
        # 기존 세션 로그아웃
        logout(request)
        
        client_id = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
        redirect_uri = request.build_absolute_uri(reverse('accounts:google_callback'))
        
        # 구글 로그인 URL로 리다이렉트
        return redirect(
            f'https://accounts.google.com/o/oauth2/v2/auth?'
            f'client_id={client_id}&'
            f'redirect_uri={redirect_uri}&'
            f'response_type=code&'
            f'scope=email profile&'
            f'prompt=select_account'
        )

class GoogleCallbackView(View):
    def get(self, request):
        try:
            code = request.GET.get('code')
            if not code:
                messages.error(request, '구글 로그인에 실패했습니다.')
                return redirect('base')

            client_id = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
            client_secret = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret']
            redirect_uri = request.build_absolute_uri(reverse('accounts:google_callback'))
            
            # 구글 토큰 받기
            token_request = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': redirect_uri,
                    'code': code,
                    'grant_type': 'authorization_code',
                }
            )
            token_json = token_request.json()
            if 'error' in token_json:
                messages.error(request, '구글 인증에 실패했습니다.')
                return redirect('base')

            access_token = token_json.get('access_token')
            if not access_token:
                messages.error(request, '구글 액세스 토큰을 받는데 실패했습니다.')
                return redirect('base')
            
            # 구글 사용자 정보 받기
            profile_request = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            profile_json = profile_request.json()
            if 'error' in profile_json:
                messages.error(request, '구글 사용자 정보를 가져오는데 실패했습니다.')
                return redirect('base')
            
            # 이메일 가져오기
            email = profile_json.get('email')
            if not email:
                messages.error(request, '이메일 정보를 가져오는데 실패했습니다.')
                return redirect('base')
            
            try:
                # 기존 사용자 찾기
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # 새 사용자 생성
                username = f"google_{profile_json.get('id')}"
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=get_random_string(length=32)
                )
                messages.success(request, '구글 계정으로 회원가입이 완료되었습니다.')
            
            # 로그인 (백엔드 명시)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, '구글 로그인이 완료되었습니다.')
            return redirect('base')
            
        except Exception as e:
            messages.error(request, '구글 로그인 중 오류가 발생했습니다.')
            return redirect('base')