from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import random
import string
from django.utils import timezone
from datetime import timedelta

# 상수 정의
NICKNAME_ADJECTIVES = [
    '행복한', '즐거운', '신나는', '귀여운', '멋진',
    '착한', '밝은', '따뜻한', '신비한', '활발한'
]

NICKNAME_NOUNS = [
    '여행자', '탐험가', '모험가', '방랑자', '여행가',
    '관광객', '백패커', '여행러', '여행꾼', '여행사'
]

MAX_NICKNAME_ATTEMPTS = 10
MAX_VERIFICATION_ATTEMPTS = 5
VERIFICATION_CODE_LENGTH = 6
VERIFICATION_EXPIRY_MINUTES = 30
PROFILE_IMAGE_SIZE = (300, 300)

def generate_random_nickname():
    """ 랜덤 닉네임 생성 """
    for _ in range(MAX_NICKNAME_ATTEMPTS):
        nickname = f"{random.choice(NICKNAME_ADJECTIVES)}{random.choice(NICKNAME_NOUNS)}{random.randint(1000, 9999)}"
        if not Profile.objects.filter(nickname=nickname).exists():
            return nickname
    raise ValueError("사용 가능한 닉네임을 생성할 수 없습니다.")

def set_unique_nicknames():
    """ 닉네임 없는 모든 프로필 처리 """
    for profile in Profile.objects.filter(nickname__isnull=True):
        try:
            profile.nickname = generate_random_nickname()
            profile.save()
        except ValueError:
            continue

class Profile(models.Model):
    """ 사용자 프로필 """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    nickname = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )
    bio = models.TextField(
        max_length=500,
        blank=True
    )
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        default='profile_images/default_profile.png'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        """ 프로필 저장 시 닉네임 생성 및 이미지 리사이징 처리 """
        if not self.nickname:
            try:
                self.nickname = generate_random_nickname()
            except ValueError:
                self.nickname = f"user_{self.user.id}"
        
        super().save(*args, **kwargs)
        
        if self.profile_image:
            try:
                self._resize_profile_image()
            except Exception as e:
                print(f"이미지 리사이징 실패: {str(e)}")

    def _resize_profile_image(self):
        """ 프로필 이미지를 PROFILE_IMAGE_SIZE 크기로 리사이징 """
        img = Image.open(self.profile_image.path)
        if img.height > PROFILE_IMAGE_SIZE[0] or img.width > PROFILE_IMAGE_SIZE[1]:
            img.thumbnail(PROFILE_IMAGE_SIZE)
            img.save(self.profile_image.path)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ 새로운 사용자 생성 시 자동 프로필 생성 """
    if created:
        Profile.objects.create(user=instance)

class EmailVerification(models.Model):
    """ 이메일 인증 """
    email = models.EmailField(unique=True)
    verification_code = models.CharField(max_length=VERIFICATION_CODE_LENGTH)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now)
    verification_attempts = models.IntegerField(default=0)
    
    @classmethod
    def generate_verification_code(cls):
        """ 랜덤 인증 코드 생성 """
        return ''.join(random.choices(string.digits, k=VERIFICATION_CODE_LENGTH))
    
    def save(self, *args, **kwargs):
        """ 저장 시 만료 시간 설정 """
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=VERIFICATION_EXPIRY_MINUTES)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """ 인증 코드 만료 확인 """
        return timezone.now() > self.expires_at
    
    def increment_attempts(self):
        """ 인증 시도 횟수 증가 """
        self.verification_attempts += 1
        self.save()
    
    def is_max_attempts_reached(self):
        """ 최대 인증 시도 횟수 도달 확인 """
        return self.verification_attempts >= MAX_VERIFICATION_ATTEMPTS
    
    def __str__(self):
        return f"{self.email} - {self.verification_code}"