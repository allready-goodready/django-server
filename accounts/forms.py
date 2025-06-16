from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '이메일 주소'})
    )
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '아이디'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '비밀번호'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '비밀번호 확인'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일 주소입니다.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')

        if password1 and email:
            # 이메일 주소에서 @ 앞부분만 추출
            email_username = email.split('@')[0]
            if email_username.lower() in password1.lower():
                raise forms.ValidationError("비밀번호는 이메일 주소와 유사할 수 없습니다.")
        
        if password1 and username:
            if username.lower() in password1.lower():
                raise forms.ValidationError("비밀번호는 아이디와 유사할 수 없습니다.")

        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname', 'bio', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        } 