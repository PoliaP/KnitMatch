from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import UserYarn

def home(request):
    """Главная страница"""
    return render(request, 'home.html')

def signup(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def user_login(request):
    """Кастомный логин (если нужно)"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    
    return render(request, 'login.html')

@login_required
def my_yarn(request):
    """Страница с пряжей пользователя"""
    yarns = UserYarn.objects.filter(user=request.user)
    return render(request, 'my_yarn.html', {'yarns': yarns})

@login_required
def add_yarn(request):
    """Добавление новой пряжи"""
    if request.method == 'POST':
        yarn_type = request.POST.get('yarn_type')
        color = request.POST.get('color')
        amount = request.POST.get('amount')
        
        if yarn_type and color and amount:
            UserYarn.objects.create(
                user=request.user,
                yarn_type=yarn_type,
                color=color,
                amount=int(amount)
            )
            return redirect('my_yarn')
    
    return render(request, 'add_yarn.html')