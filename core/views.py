from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
try:
    from django.utils.http import is_safe_url
except ImportError:
    # для старых версий Django
    from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
from .forms import LoginForm, SignupForm, ProfileForm
from .models import Profile

def login_view(request):
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if next_url and is_safe_url(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect('/')
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form, 'next': next_url})

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('/')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    next_url = request.GET.get('next', '')
    if next_url and is_safe_url(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('/')

@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('core:profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, 'core/profile.html', {'form': form})