from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=150)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class SignupForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ('avatar',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'name'):
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
            ext = avatar.name.rsplit('.', 1)[-1].lower() if '.' in avatar.name else ''
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Недопустимый формат. Разрешены: {", ".join(sorted(allowed_extensions))}'
                )
            max_size = 5 * 1024 * 1024  # 5 MB
            if avatar.size > max_size:
                raise forms.ValidationError('Размер файла не должен превышать 5 МБ.')
        return avatar

    def save(self, commit=True):
        if self.user:
            self.user.username = self.cleaned_data['username']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        profile = super().save(commit=commit)
        return profile