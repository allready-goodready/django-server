from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError
import logging
import random
import string

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def _generate_unique_username(self, base_username=None):
        """프로필 기본 닉네임 랜덤 생성"""
        try:
            if base_username:
                username = base_username
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{random.randint(1000, 9999)}"
            else:
                while True:
                    username = f"user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
                    if not User.objects.filter(username=username).exists():
                        break
            return username
        except Exception as e:
            logger.error(f"사용자 이름 생성 중 오류 발생: {str(e)}")
            raise

    def pre_social_login(self, request, sociallogin):
        """기존 사용자 확인 및 소셜 계정 연결"""
        try:
            user = sociallogin.user
            if user.id:
                return

            if not user.email:
                logger.warning("이메일이 없는 소셜 로그인 시도")
                raise ValidationError("이메일 정보가 필요합니다.")

            try:
                existing_user = User.objects.get(email=user.email)
                sociallogin.connect(request, existing_user)
                logger.info(f"기존 사용자 연결 성공: {user.email}")
            except User.DoesNotExist:
                logger.info(f"새로운 사용자 등록: {user.email}")
            except DatabaseError as e:
                logger.error(f"데이터베이스 오류 발생: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"소셜 로그인 처리 중 오류 발생: {str(e)}")
            raise

    def is_auto_signup_allowed(self, request, sociallogin):
        try:
            return True
        except Exception as e:
            logger.error(f"자동 가입 확인 중 오류 발생: {str(e)}")
            return False

    def populate_user(self, request, sociallogin, data):
        """사용자 정보를 채우는 메서드"""
        try:
            user = super().populate_user(request, sociallogin, data)
            
            if sociallogin.account.provider == 'kakao':
                try:
                    kakao_account = sociallogin.account.extra_data.get('kakao_account', {})
                    email = kakao_account.get('email')
                    
                    if email:
                        try:
                            existing_user = User.objects.get(email=email)
                            user = existing_user
                            logger.info(f"기존 사용자 정보 사용: {email}")
                        except User.DoesNotExist:
                            base_username = email.split('@')[0]
                            user.username = self._generate_unique_username(base_username)
                            logger.info(f"새로운 사용자 이름 생성: {user.username}")
                    else:
                        user.username = self._generate_unique_username()
                        logger.info(f"이메일 없는 사용자 이름 생성: {user.username}")
                except KeyError as e:
                    logger.error(f"카카오 계정 데이터 접근 오류: {str(e)}")
                    raise
                except Exception as e:
                    logger.error(f"카카오 사용자 정보 처리 중 오류: {str(e)}")
                    raise

            return user
        except Exception as e:
            logger.error(f"사용자 정보 채우기 중 오류 발생: {str(e)}")
            raise

    def save_user(self, request, sociallogin, form=None):
        """사용자 저장 메서드"""
        try:
            user = super().save_user(request, sociallogin, form)
            
            try:
                if not hasattr(user, 'profile'):
                    from .models import Profile
                    Profile.objects.create(user=user)
                    logger.info(f"새로운 프로필 생성 완료: {user.username}")
            except IntegrityError as e:
                logger.error(f"프로필 생성 중 무결성 오류: {str(e)}")
                raise
            except DatabaseError as e:
                logger.error(f"프로필 생성 중 데이터베이스 오류: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"프로필 생성 중 예상치 못한 오류: {str(e)}")
                raise
                
            return user
        except Exception as e:
            logger.error(f"사용자 저장 중 오류 발생: {str(e)}")
            raise 