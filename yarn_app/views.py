from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import UserYarn, Pattern, Project, ProjectYarn, Favorite
from .ravelry_api import RavelryAPI, get_yarn_type_mapping

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
        if yarn.weight:
            total_weight += yarn.amount * yarn.weight
    
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
def yarn_detail(request, yarn_id):
    """Детальная информация о пряже"""
    try:
        yarn = UserYarn.objects.get(id=yarn_id, user=request.user)
        
        # Рассчитываем общий вес для этой карточки
        total_weight = 0
        if yarn.weight:
            total_weight = yarn.amount * yarn.weight
        
        context = {
            'yarn': yarn,
            'total_weight': total_weight,
        }
        
        return render(request, 'yarn_detail.html', context)
    except UserYarn.DoesNotExist:
        return redirect('my_yarn')

@login_required
def yarn_projects(request, yarn_id):
    """Поиск проектов для конкретной пряжи"""
    yarn = get_object_or_404(UserYarn, id=yarn_id, user=request.user)
    
    # Получаем соответствующие веса пряжи для Ravelry
    type_mapping = get_yarn_type_mapping()
    ravelry_weights = type_mapping.get(yarn.yarn_type, [])
    
    # Ищем схемы
    matching_patterns = Pattern.objects.none()
    for weight in ravelry_weights:
        patterns = Pattern.objects.filter(
            Q(yarn_weight__icontains=weight)
        )
        matching_patterns = matching_patterns | patterns
    
    # Убираем дубликаты и сортируем по рейтингу
    matching_patterns = matching_patterns.distinct().order_by('-rating')[:20]
    
    # Получаем все избранные схемы пользователя
    favorite_pattern_ids = Favorite.objects.filter(
        user=request.user,
        pattern__in=matching_patterns
    ).values_list('pattern_id', flat=True)
    
    context = {
        'yarn': yarn,
        'patterns': matching_patterns,
        'favorite_pattern_ids': list(favorite_pattern_ids),
        'search_message': f"Найдено {matching_patterns.count()} схем для пряжи: {yarn.get_yarn_type_display()}"
    }
    
    return render(request, 'yarn_projects.html', context)

@login_required
def use_in_project(request, yarn_id):
    """Добавить пряжу в проект (заглушка)"""
    return redirect('my_yarn')

@login_required
def projects(request):
    """Страница проектов и схем"""
    # ВАЖНО: Берем ВСЕ схемы из базы
    all_patterns = Pattern.objects.all().order_by('-id')  # Сначала новые
    
    # Фильтрация
    difficulty_filter = request.GET.get('difficulty', '')
    yarn_weight_filter = request.GET.get('yarn_weight', '')
    search_query = request.GET.get('search', '')
    
    patterns = all_patterns
    
    if difficulty_filter:
        patterns = patterns.filter(difficulty=difficulty_filter)
    
    if yarn_weight_filter:
        patterns = patterns.filter(yarn_weight__icontains=yarn_weight_filter)
    
    if search_query:
        patterns = patterns.filter(name__icontains=search_query)

    """Страница проектов и схем"""
    user_projects = Project.objects.filter(user=request.user).order_by('-created_at')
    
    # ПОЛУЧАЕМ СХЕМЫ ИЗ БАЗЫ (вместо "свежих схем из API")
    all_patterns = Pattern.objects.all().order_by('-created_at')
    
    # Фильтрация схем
    difficulty_filter = request.GET.get('difficulty', '')
    yarn_weight_filter = request.GET.get('yarn_weight', '')
    search_query = request.GET.get('search', '')
    
    patterns = all_patterns
    
    if difficulty_filter:
        patterns = patterns.filter(difficulty=difficulty_filter)
    
    if yarn_weight_filter:
        patterns = patterns.filter(yarn_weight__icontains=yarn_weight_filter)
    
    if search_query:
        patterns = patterns.filter(name__icontains=search_query)
    
    # Ограничиваем количество если нужно
    patterns = patterns[:50]
    
    # Получаем избранные схемы
    favorite_pattern_ids = []
    if request.user.is_authenticated:
        favorite_pattern_ids = Favorite.objects.filter(
            user=request.user,
            pattern__in=patterns
        ).values_list('pattern_id', flat=True)
    
    # Статистика проектов
    projects_stats = {
        'total': user_projects.count(),
        'planned': user_projects.filter(status='planned').count(),
        'in_progress': user_projects.filter(status='in_progress').count(),
        'completed': user_projects.filter(status='completed').count(),
    }
    
    # Анализ пряжи пользователя
    user_yarns = UserYarn.objects.filter(user=request.user)
    
    yarn_analysis = {
        'by_type': {},
        'total_yarns': user_yarns.count(),
        'total_motki': 0,
        'total_weight': 0,
        'colors_count': 0,
        'types_count': 0,
    }
    
    colors_set = set()
    types_set = set()
    
    for yarn in user_yarns:
        yarn_weight = yarn.total_weight
        yarn_analysis['total_weight'] += yarn_weight
        yarn_analysis['total_motki'] += yarn.amount
        colors_set.add(yarn.color)
        types_set.add(yarn.yarn_type)
        
        type_display = yarn.get_yarn_type_display()
        if type_display not in yarn_analysis['by_type']:
            yarn_analysis['by_type'][type_display] = {
                'amount': 0,
                'total_weight': 0
            }
        
        yarn_analysis['by_type'][type_display]['amount'] += yarn.amount
        yarn_analysis['by_type'][type_display]['total_weight'] += yarn_weight
    
    yarn_analysis['colors_count'] = len(colors_set)
    yarn_analysis['types_count'] = len(types_set)
    
    # Собираем уникальные веса пряжи для фильтра
    yarn_weights = Pattern.objects.values_list('yarn_weight', flat=True).distinct()
    
    context = {
        'projects': user_projects,
        'patterns': patterns,  # Теперь передаем отфильтрованные схемы
        'favorite_pattern_ids': list(favorite_pattern_ids),
        'stats': projects_stats,
        'yarn_analysis': yarn_analysis,
        'difficulty_filter': difficulty_filter,
        'yarn_weight_filter': yarn_weight_filter,
        'search_query': search_query,
        'yarn_weights': sorted(set(yarn_weights)),
        'difficulty_choices': [
            ('', 'Любая сложность'),
            ('beginner', 'Начинающий'),
            ('easy', 'Легкий'),
            ('intermediate', 'Средний'),
            ('experienced', 'Опытный'),
        ],
        'total_patterns': patterns.count(),
    }
    
    return render(request, 'projects.html', context)

@login_required
def project_detail(request, project_id):
    """Детальная страница проекта"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    project_yarns = ProjectYarn.objects.filter(project=project)
    
    # Считаем использованную пряжу
    used_yarn_stats = {
        'total_motki': 0,
        'total_weight': 0,
    }
    
    for project_yarn in project_yarns:
        yarn = project_yarn.user_yarn
        used_yarn_stats['total_motki'] += project_yarn.amount_used
        if yarn.weight:
            used_yarn_stats['total_weight'] += project_yarn.amount_used * yarn.weight
    
    context = {
        'project': project,
        'project_yarns': project_yarns,
        'used_yarn_stats': used_yarn_stats,
    }
    
    return render(request, 'project_detail.html', context)

@login_required
def add_project(request):
    """Создание нового проекта"""
    user_yarns = UserYarn.objects.filter(user=request.user)
    
    # Получаем ID схемы из GET параметров (если перешли с поиска)
    pattern_id = request.GET.get('pattern')
    initial_pattern = None
    if pattern_id:
        try:
            initial_pattern = Pattern.objects.get(id=pattern_id)
        except Pattern.DoesNotExist:
            pass
    
    if request.method == 'POST':
        name = request.POST.get('name')
        pattern_id = request.POST.get('pattern')
        status = request.POST.get('status', 'planned')
        description = request.POST.get('description', '')
        
        if name:
            project = Project.objects.create(
                user=request.user,
                name=name,
                pattern_id=pattern_id if pattern_id else None,
                status=status,
                description=description,
            )
            
            # Добавляем пряжу к проекту
            for yarn in user_yarns:
                amount_key = f'yarn_{yarn.id}'
                amount_used = request.POST.get(amount_key, '0')
                
                if amount_used and int(amount_used) > 0:
                    ProjectYarn.objects.create(
                        project=project,
                        user_yarn=yarn,
                        amount_used=int(amount_used)
                    )
            
            return redirect('project_detail', project_id=project.id)
    
    # Получаем рекомендации схем
    recommended_patterns = get_recommended_patterns(request.user)
    
    context = {
        'user_yarns': user_yarns,
        'recommended_patterns': recommended_patterns,
        'initial_pattern': initial_pattern,
        'status_choices': Project.STATUS_CHOICES,
    }
    
    return render(request, 'add_project.html', context)

@login_required
def delete_project(request, project_id):
    """Удаление проекта"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    if request.method == 'POST':
        project.delete()
        return redirect('projects')
    
    return render(request, 'delete_project.html', {'project': project})

@login_required
def pattern_search(request):
    """Поиск подходящих схем"""
    user_yarns = UserYarn.objects.filter(user=request.user)
    
    # Получаем все уникальные типы пряжи пользователя
    user_yarn_types = set(user_yarns.values_list('yarn_type', flat=True))
    
    # Поиск подходящих схем
    suitable_patterns = Pattern.objects.none()
    for yarn_type in user_yarn_types:
        patterns = get_patterns_by_yarn_type(yarn_type)
        suitable_patterns = suitable_patterns | patterns
    
    # Убираем дубликаты
    suitable_patterns = suitable_patterns.distinct()
    
    # Если нет подходящих, показываем все
    if not suitable_patterns.exists():
        suitable_patterns = Pattern.objects.all()
    
    # Фильтры
    difficulty_filter = request.GET.get('difficulty', '')
    search_query = request.GET.get('search', '')
    free_only = request.GET.get('free', '')
    
    if difficulty_filter:
        suitable_patterns = suitable_patterns.filter(difficulty=difficulty_filter)
    
    if search_query:
        suitable_patterns = suitable_patterns.filter(name__icontains=search_query)
    
    if free_only:
        suitable_patterns = suitable_patterns.filter(is_free=True)
    
    # Ограничиваем количество
    suitable_patterns = suitable_patterns.order_by('-rating')[:50]

    favorite_pattern_ids = Favorite.objects.filter(
        user=request.user,
        pattern__in=suitable_patterns
    ).values_list('pattern_id', flat=True)

    context = {
        'patterns': suitable_patterns,
        'favorite_ids': list(favorite_pattern_ids),
        'user_yarns': user_yarns,
        'favorite_pattern_ids': list(favorite_pattern_ids), 
        'difficulty_filter': difficulty_filter,
        'search_query': search_query,
        'free_only': free_only,
        'difficulty_choices': [
            ('', 'Любая сложность'),
            ('beginner', 'Начинающий'),
            ('easy', 'Легкий'),
            ('intermediate', 'Средний'),
            ('experienced', 'Опытный'),
        ]
    }
    
    return render(request, 'projects.html', context)

@login_required
def toggle_favorite(request, pattern_id):
    """Добавление/удаление схемы из избранного"""
    pattern = get_object_or_404(Pattern, id=pattern_id)
    
    try:
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            pattern=pattern
        )
        
        if not created:
            # Удаляем из избранного
            favorite.delete()
            message = "Схема удалена из избранного"
            is_favorite = False
        else:
            # Добавляем в избранное
            message = "Схема добавлена в избранное"
            is_favorite = True
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success', 
                'message': message,
                'is_favorite': is_favorite
            })
        else:
            return redirect('pattern_search')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            })
        else:
            return redirect('pattern_search')

@login_required
def favorites(request):
    """Страница избранных схем"""
    print(f"[DEBUG] Пользователь: {request.user.username}")
    
    # Получаем избранные схемы пользователя
    favorite_patterns = Pattern.objects.filter(
        favorite__user=request.user
    ).distinct()
    
    print(f"[DEBUG] Найдено схем: {favorite_patterns.count()}")
    
    # Выводим в консоль что нашли
    for pattern in favorite_patterns:
        print(f"[DEBUG] - {pattern.name} (ID: {pattern.id})")
    
    context = {
        'patterns': favorite_patterns,
    }
    
    return render(request, 'favorites.html', context)

@login_required
def load_more_patterns(request):
    """AJAX загрузка дополнительных схем"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        count, _ = RavelryAPI.fetch_popular_patterns(count=5)
        
        if count > 0:
            # Получаем последние добавленные схемы
            new_patterns = Pattern.objects.order_by('-created_at')[:5]
            
            patterns_data = []
            for pattern in new_patterns:
                patterns_data.append({
                    'id': pattern.id,
                    'name': pattern.name,
                    'yarn_weight': pattern.yarn_weight,
                    'photo_url': pattern.photo_url,
                    'difficulty': pattern.get_difficulty_display(),
                    'is_free': pattern.is_free,
                    'rating': pattern.rating,
                    'pattern_url': pattern.pattern_url,
                })
            
            return JsonResponse({
                'success': True,
                'patterns': patterns_data,
                'count': len(patterns_data)
            })
    
    return JsonResponse({'success': False})

@login_required
def refresh_patterns(request):
    """Обновление базы схем"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        count, _ = RavelryAPI.fetch_popular_patterns(count=10)
        
        return JsonResponse({
            'success': True,
            'message': f'Загружено {count} новых схем'
        })
    
    return redirect('pattern_search')

# Вспомогательные функции
def get_recommended_patterns(user):
    """Получение рекомендованных схем для пользователя"""
    user_yarns = UserYarn.objects.filter(user=user)
    
    if not user_yarns.exists():
        return Pattern.objects.all()[:10]
    
    # Получаем самый распространенный тип пряжи
    yarn_type_counts = {}
    for yarn in user_yarns:
        yarn_type = yarn.yarn_type
        yarn_type_counts[yarn_type] = yarn_type_counts.get(yarn_type, 0) + 1
    
    if yarn_type_counts:
        # Находим самый частый тип пряжи
        most_common_type = max(yarn_type_counts.items(), key=lambda x: x[1])[0]
        return get_patterns_by_yarn_type(most_common_type)[:10]
    
    return Pattern.objects.all()[:10]

def get_patterns_by_yarn_type(yarn_type):
    """Получение схем по типу пряжи"""
    type_mapping = get_yarn_type_mapping()
    ravelry_weights = type_mapping.get(yarn_type, [])
    
    matching_patterns = Pattern.objects.none()
    for weight in ravelry_weights:
        patterns = Pattern.objects.filter(yarn_weight__icontains=weight)
        matching_patterns = matching_patterns | patterns
    
    return matching_patterns.distinct().order_by('-rating')