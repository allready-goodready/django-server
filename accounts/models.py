from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import random
import string

def generate_random_nickname():
    adjectives = ['행복한', '즐거운', '신나는', '귀여운', '멋진', '착한', '밝은', '따뜻한', '신비한', '활발한']
    nouns = ['여행자', '탐험가', '모험가', '방랑자', '여행가', '관광객', '백패커', '여행러', '여행꾼', '여행사']
    
    while True:
        nickname = f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(1000, 9999)}"
        if not Profile.objects.filter(nickname=nickname).exists():
            return nickname

def set_unique_nicknames():
    profiles = Profile.objects.all()
    for profile in profiles:
        if not profile.nickname:
            profile.nickname = generate_random_nickname()
            profile.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=50, unique=True, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        default='profile_images/default_profile.png'  # media/profile_images/에 파일 필요
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = generate_random_nickname()
        super().save(*args, **kwargs)
        
        if self.profile_image:
            img = Image.open(self.profile_image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_image.path)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    verification_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def generate_verification_code(cls):
        return ''.join(random.choices(string.digits, k=6))
    
    def __str__(self):
        return f"{self.email} - {self.verification_code}"