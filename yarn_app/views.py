# views.py - обновленная версия без редактирования
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
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
def logout_view(request):
    """Выход из системы"""
    auth_logout(request)
    return redirect('home')

@login_required
def my_yarn(request):
    """Страница с пряжей пользователя"""
    yarns = UserYarn.objects.filter(user=request.user).order_by('-created_at')
    
    # Рассчитываем статистику
    total_yarns = yarns.count()
    total_motki = sum(yarn.amount for yarn in yarns)
    
    # Считаем ОБЩИЙ ВЕС: количество мотков × вес одного мотка
    total_weight = 0
    for yarn in yarns:
        try:
            if hasattr(yarn, 'weight') and yarn.weight:
                # Умножаем количество мотков на вес одного мотка
                total_weight += yarn.amount * yarn.weight
        except:
            pass
    
    # Получаем уникальные цвета
    colors_set = set()
    for yarn in yarns:
        colors_set.add(yarn.color)
    
    # Получаем уникальные типы пряжи
    types_set = set()
    for yarn in yarns:
        types_set.add(yarn.yarn_type)
    
    context = {
        'yarns': yarns,
        'total_yarns': total_yarns,
        'total_motki': total_motki,
        'total_weight': total_weight,
        'colors_count': len(colors_set),
        'types_count': len(types_set),
    }
    
    return render(request, 'my_yarn.html', context)

@login_required
def add_yarn(request):
    """Добавление новой пряжи"""
    # Палитра цветов
    color_choices = [
        ('#FF6B8B', 'Розовый'),
        ('#8A4FFF', 'Фиолетовый'),
        ('#00D4AA', 'Бирюзовый'),
        ('#4FC3F7', 'Голубой'),
        ('#FFA726', 'Оранжевый'),
        ('#66BB6A', 'Зеленый'),
        ('#FFEB3B', 'Желтый'),
        ('#795548', 'Коричневый'),
        ('#9E9E9E', 'Серый'),
        ('#000000', 'Черный'),
        ('#FFFFFF', 'Белый'),
    ]
    
    # Типы пряжи из модели
    YARN_TYPES_CHOICES = [
        ('fingering', 'Тонкая (Fingering)'),
        ('sport', 'Спортивная (Sport)'),
        ('dk', 'Средняя (DK)'),
        ('worsted', 'Камвольная (Worsted)'),
        ('bulky', 'Толстая (Bulky)'),
        ('other', 'Другая'),
    ]
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        yarn_type = request.POST.get('yarn_type')
        color = request.POST.get('color')
        amount = request.POST.get('amount')
        weight = request.POST.get('weight')
        manufacturer = request.POST.get('manufacturer', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        if yarn_type and color and amount:
            UserYarn.objects.create(
                user=request.user,
                name=name if name else None,
                yarn_type=yarn_type,
                color=color,
                amount=int(amount),
                weight=int(weight) if weight else None,
                manufacturer=manufacturer if manufacturer else None,
                notes=notes if notes else None
            )
            return redirect('my_yarn')
    
    return render(request, 'add_yarn.html', {
        'color_choices': color_choices,
        'yarn_types': YARN_TYPES_CHOICES
    })

@login_required
def delete_yarn(request, yarn_id):
    """Удаление пряжи"""
    yarn = get_object_or_404(UserYarn, id=yarn_id, user=request.user)
    
    if request.method == 'POST':
        yarn.delete()
        return redirect('my_yarn')
    
    return render(request, 'delete_yarn.html', {'yarn': yarn})

@login_required
def use_in_project(request, yarn_id):
    """Добавить пряжу в проект (заглушка)"""
    # Пока просто редирект обратно
    return redirect('my_yarn')

@login_required
def yarn_detail(request, yarn_id):
    """Детальная информация о пряже"""
    try:
        yarn = UserYarn.objects.get(id=yarn_id, user=request.user)
        return render(request, 'yarn_detail.html', {'yarn': yarn})
    except UserYarn.DoesNotExist:
        return redirect('my_yarn')
    
# Дополнительные страницы (заглушки)
def projects(request):
    """Страница проектов"""
    return render(request, 'projects.html')

def favorites(request):
    """Страница избранного"""
    return render(request, 'favorites.html')