# Django 기본
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse

# 앱 모델 및 폼
from .models import Profile, EmailVerification
from .forms import ProfileUpdateForm, SignUpForm

# 인증 백엔드
from django.contrib.auth.backends import ModelBackend

# 소셜 로그인
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView, OAuth2CallbackView
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.kakao.provider import KakaoProvider

# 기타 Django
from django.conf import settings
from django.views.generic import View
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail

import requests

User = get_user_model()

def base(request):
    # 기본 페이지 뷰
    signup_completed = request.session.pop('signup_completed', False)
    return render(request, 'base.html', {'signup_completed': signup_completed})

@require_http_methods(['POST'])
def send_verification_email(request):
    # 이메일 인증 코드
    try:
        email = request.POST.get('email')
        if not email:
            return JsonResponse({
                'status': 'error',
                'message': '이메일을 입력해주세요.'
            })
        
        # 이메일 중복 체크
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'status': 'error',
                'message': '이미 사용 중인 이메일입니다.'
            })
        
        # 인증 코드 생성
        verification_code = EmailVerification.generate_verification_code()
        
        # 기존 인증 정보가 있다면 업데이트
        verification, created = EmailVerification.objects.update_or_create(
            email=email,
            defaults={
                'verification_code': verification_code,
                'is_verified': False
            }
        )
        
        # 이메일 전송
        subject = '이메일 인증 코드'
        message = f'회원가입을 위한 인증 코드는 {verification_code} 입니다.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        send_mail(subject, message, from_email, recipient_list)
        return JsonResponse({
            'status': 'success',
            'message': '인증 코드가 이메일로 전송되었습니다.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': '이메일 전송 중 오류가 발생했습니다.',
            'error': str(e)
        })

@require_http_methods(['POST'])
def verify_email(request):
    # 이메일 인증 코드 확인
    try:
        email = request.POST.get('email')
        code = request.POST.get('code')
        
        if not email or not code:
            return JsonResponse({
                'status': 'error',
                'message': '이메일과 인증 코드를 모두 입력해주세요.'
            })
        
        try:
            verification = EmailVerification.objects.get(
                email=email,
                verification_code=code
            )
            verification.is_verified = True
            verification.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '이메일 인증이 완료되었습니다.'
            })
        except EmailVerification.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '잘못된 인증 코드입니다.'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': '이메일 인증 중 오류가 발생했습니다.',
            'error': str(e)
        })

def login_user(request, user):
    # 사용자 로그인
    return login(request, user, backend='django.contrib.auth.backends.ModelBackend')

@require_http_methods(['GET', 'POST'])
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # 사용자 이름 중복 체크를 먼저 수행
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': '이미 사용 중인 아이디입니다.'
                })
            
            # 이메일 인증 확인
            try:
                verification = EmailVerification.objects.get(
                    email=form.cleaned_data['email'],
                    is_verified=True
                )
            except EmailVerification.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': '이메일 인증이 필요합니다.'
                })
            
            try:
                # 사용자 생성
                user = form.save()
                
                # 로그인
                login_user(request, user)
                
                # 이메일 인증 정보 삭제
                verification.delete()
                
                # 성공 응답 전송
                response = JsonResponse({
                    'status': 'success',
                    'message': '회원가입이 완료되었습니다.',
                    'redirect_url': '/base/'
                })
                
                # 세션에 회원가입 완료 플래그 설정
                request.session['signup_completed'] = True
                
                return response
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': '회원가입 중 오류가 발생했습니다.',
                    'errors': str(e)
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '입력하신 정보를 확인해주세요.',
                'errors': form.errors
            })
    
    form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def signin_view(request):
    # 로그인 처리
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': '로그인되었습니다.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '아이디 또는 비밀번호가 올바르지 않습니다.'
            })
    return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'})

@login_required
def signout_view(request):
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('base')

@login_required
def profile_view(request):
    user = request.user
    active_tab = request.GET.get('tab', 'feeds')
    
    context = {
        'user': user,
        'active_tab': active_tab,
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def update_profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'accounts/profile_update.html', {'form': form})

@login_required
def user_activities_view(request):
    user = request.user
    # 사용자의 활동 내역을 가져오기
    # ex) 작성글, 좋아요 글 등
    return render(request, 'accounts/activities.html', {
        'message': '활동 내역 조회 기능은 추후 구현 예정'
    })

def kakao_login(request):
    # 기존 세션 로그아웃
    logout(request)
    
    # 카카오 로그아웃 처리
    client_id = settings.SOCIALACCOUNT_PROVIDERS['kakao']['APP']['client_id']
    redirect_uri = request.build_absolute_uri(reverse('accounts:kakao_callback'))
    
    # 카카오 로그인 URL로 리다이렉트
    return redirect(
        f'https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&prompt=login'
    )

def kakao_callback(request):
    try:
        code = request.GET.get('code')
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
        access_token = token_json.get('access_token')
        
        # 카카오 사용자 정보 받기
        profile_request = requests.get(
            'https://kapi.kakao.com/v2/user/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        profile_json = profile_request.json()
        kakao_account = profile_json.get('kakao_account')
        
        # 이메일 가져오기
        email = kakao_account.get('email')
        
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
        
        # 로그인 (백엔드 명시)
        login_user(request, user)
        return redirect('base')
        
    except Exception as e:
        print(f"카카오 로그인 오류: {str(e)}")
        return redirect('base')

def google_login(request):
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

def google_callback(request):
    try:
        code = request.GET.get('code')
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
        access_token = token_json.get('access_token')
        
        # 구글 사용자 정보 받기
        profile_request = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        profile_json = profile_request.json()
        
        # 이메일 가져오기
        email = profile_json.get('email')
        
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
        
        # 로그인 (백엔드 명시)
        login_user(request, user)
        return redirect('base')
        
    except Exception as e:
        print(f"구글 로그인 오류: {str(e)}")
        return redirect('base')