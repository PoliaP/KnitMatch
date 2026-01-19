from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import UserYarn, Pattern, Project, ProjectYarn, Favorite
from .ravelry_api import ravelry_personal, get_yarn_type_mapping

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
    matching_patterns = matching_patterns.distinct().order_by('-rating')
    
    # Пагинация - 20 схем на страницу
    paginator = Paginator(matching_patterns, 20)
    page = request.GET.get('page', 1)
    
    try:
        patterns_page = paginator.page(page)
    except PageNotAnInteger:
        patterns_page = paginator.page(1)
    except EmptyPage:
        patterns_page = paginator.page(paginator.num_pages)
    
    # Получаем все избранные схемы пользователя
    favorite_pattern_ids = Favorite.objects.filter(
        user=request.user,
        pattern__in=matching_patterns
    ).values_list('pattern_id', flat=True)
    
    context = {
        'yarn': yarn,
        'patterns': patterns_page,
        'favorite_pattern_ids': list(favorite_pattern_ids),
        'search_message': f"Найдено {matching_patterns.count()} схем для пряжи: {yarn.get_yarn_type_display()}",
        'paginator': paginator,
        'page_obj': patterns_page,
    }
    
    return render(request, 'yarn_projects.html', context)

@login_required
def use_in_project(request, yarn_id):
    """Добавить пряжу в проект (заглушка)"""
    return redirect('my_yarn')

@login_required
def projects(request):
    """Страница проектов и схем"""
    user_projects = Project.objects.filter(user=request.user).order_by('-created_at')
    
    # Получаем схемы из базы
    all_patterns = Pattern.objects.all().order_by('-created_at')
    
    # Фильтрация схем
    difficulty_filter = request.GET.get('difficulty', '')
    yarn_weight_filter = request.GET.get('yarn_weight', '')
    search_query = request.GET.get('search', '')
    
    # ДОБАВЛЕНЫ НОВЫЕ ФИЛЬТРЫ
    free_only = request.GET.get('free_only') == 'true'
    with_photos = request.GET.get('with_photos') == 'true'
    high_rated = request.GET.get('high_rated') == 'true'
    
    patterns = all_patterns
    
    if difficulty_filter:
        patterns = patterns.filter(difficulty=difficulty_filter)
    
    if yarn_weight_filter:
        patterns = patterns.filter(yarn_weight__icontains=yarn_weight_filter)
    
    if search_query:
        patterns = patterns.filter(name__icontains=search_query)
    
    # ПРИМЕНЯЕМ НОВЫЕ ФИЛЬТРЫ
    if free_only:
        patterns = patterns.filter(is_free=True)
    
    if with_photos:
        patterns = patterns.exclude(photo_url='').exclude(photo_url__isnull=True)
    
    if high_rated:
        patterns = patterns.filter(rating__gte=4.0)
    
    # Пагинация - 20 схем на страницу
    paginator = Paginator(patterns, 20)
    page = request.GET.get('page', 1)
    
    try:
        patterns_page = paginator.page(page)
    except PageNotAnInteger:
        patterns_page = paginator.page(1)
    except EmptyPage:
        patterns_page = paginator.page(paginator.num_pages)
    
    # Получаем избранные схемы
    favorite_pattern_ids = []
    if request.user.is_authenticated:
        favorite_pattern_ids = Favorite.objects.filter(
            user=request.user,
            pattern__in=patterns_page
        ).values_list('pattern_id', flat=True)
    
    # Собираем уникальные веса пряжи для фильтра
    yarn_weights = Pattern.objects.values_list('yarn_weight', flat=True).distinct()
    
    # Передаем параметры фильтров в контекст для сохранения состояния чекбоксов
    context = {
        'projects': user_projects,
        'patterns': patterns_page,
        'favorite_pattern_ids': list(favorite_pattern_ids),
        'difficulty_filter': difficulty_filter,
        'yarn_weight_filter': yarn_weight_filter,
        'search_query': search_query,
        'free_only': free_only,  # ДОБАВЛЕНО
        'with_photos': with_photos,  # ДОБАВЛЕНО
        'high_rated': high_rated,  # ДОБАВЛЕНО
        'yarn_weights': sorted(set(yarn_weights)),
        'difficulty_choices': [
            ('', 'Любая сложность'),
            ('beginner', 'Начинающий'),
            ('easy', 'Легкий'),
            ('intermediate', 'Средний'),
            ('experienced', 'Опытный'),
        ],
        'total_patterns': patterns.count(),
        'paginator': paginator,
        'page_obj': patterns_page,
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
    
    # Пагинация - 20 схем на страницу
    paginator = Paginator(suitable_patterns.order_by('-rating'), 20)
    page = request.GET.get('page', 1)
    
    try:
        patterns_page = paginator.page(page)
    except PageNotAnInteger:
        patterns_page = paginator.page(1)
    except EmptyPage:
        patterns_page = paginator.page(paginator.num_pages)

    favorite_pattern_ids = Favorite.objects.filter(
        user=request.user,
        pattern__in=patterns_page
    ).values_list('pattern_id', flat=True)

    context = {
        'patterns': patterns_page,
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
        ],
        'paginator': paginator,
        'page_obj': patterns_page,
    }
    
    return render(request, 'pattern_search.html', context)

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
            return redirect(request.META.get('HTTP_REFERER', 'projects'))
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            })
        else:
            return redirect(request.META.get('HTTP_REFERER', 'projects'))

@login_required
def favorites(request):
    """Страница избранных схем"""
    
    # Получаем избранные схемы пользователя
    favorite_patterns = Pattern.objects.filter(
        favorite__user=request.user
    ).distinct()
    
    # Пагинация - 20 схем на страницу
    paginator = Paginator(favorite_patterns, 20)
    page = request.GET.get('page', 1)
    
    try:
        patterns_page = paginator.page(page)
    except PageNotAnInteger:
        patterns_page = paginator.page(1)
    except EmptyPage:
        patterns_page = paginator.page(paginator.num_pages)
    
    context = {
        'patterns': patterns_page,
        'paginator': paginator,
        'page_obj': patterns_page,
    }
    
    return render(request, 'favorites.html', context)

def get_pattern_url_from_ravelry(ravelry_id):
    """Создает корректный URL для схемы на Ravelry"""
    if not ravelry_id:
        return '#'
    
    # Проверяем, является ли ravelry_id числом
    try:
        pattern_id = int(ravelry_id)
        return f'https://www.ravelry.com/patterns/library/{pattern_id}'
    except (ValueError, TypeError):
        # Если это не число (например, test_1234), используем альтернативный формат
        return f'https://www.ravelry.com/patterns/search#pattern={ravelry_id}'

@csrf_exempt
@login_required
def refresh_patterns(request):
    """Загружает случайные схемы из Ravelry"""
    
    try:
        count = int(request.POST.get('count', 6))
        
        # 1. Пробуем загрузить случайные схемы
        try:
            connected = ravelry_personal.test_connection()
            
            if connected:
                # Получаем случайные схемы вместо популярных
                patterns_data = get_random_patterns(count)
                
                if patterns_data and len(patterns_data) > 0:
                    return save_real_patterns(patterns_data, count)
        except Exception as api_error:
            print(f"⚠ Ошибка API: {api_error}")
        
        # 2. Если API не сработал - тестовые схемы
        return create_test_patterns(count)
        
    except Exception as e:
        return create_test_patterns(6)

def get_random_patterns(count):
    """Получает случайные схемы из Ravelry"""
    import random
    
    # Параметры для поиска с разными запросами
    search_queries = [
        '',  # Пустой запрос
        'sweater', 'shawl', 'hat', 'socks',
        'mittens', 'scarf', 'cardigan', 'blanket',
        'baby', 'cable', 'lace', 'colorwork'
    ]
    
    yarn_weights = [
        '',  # Любая пряжа
        'fingering', 'sport', 'dk', 'worsted', 'bulky'
    ]
    
    # Выбираем случайные параметры
    query = random.choice(search_queries)
    yarn_weight = random.choice(yarn_weights)
    page = random.randint(1, 10)  # Берем со случайной страницы
    
    params = {
        'page_size': min(count, 50),
        'page': page,
        'craft': 'knitting'
    }
    
    if query:
        params['query'] = query
    if yarn_weight:
        params['weight'] = yarn_weight
    
    # Делаем запрос к API
    data = ravelry_personal._make_request('patterns/search.json', params)
    
    if not data or 'patterns' not in data:
        return []
    
    patterns = data.get('patterns', [])
    
    if not patterns:
        return []
    
    # Перемешиваем результаты
    random.shuffle(patterns)
    
    return patterns[:count]

def create_ravelry_url(pattern_data, ravelry_id):
    """Создает правильный URL для схемы на Ravelry"""

    permalink = pattern_data.get('permalink')
    
    if permalink and isinstance(permalink, str):
        permalink = permalink.strip()
        
        # Если это уже полный URL
        if permalink.startswith('http'):
            return permalink
        
        # Если это путь Ravelry (начинается с /patterns/)
        elif permalink.startswith('/patterns/'):
            result = f'https://www.ravelry.com{permalink}'
            return result
        
        # Если это просто slug без слэша (например "ultimate-mittens")
        elif not permalink.startswith('/'):
            # Проверим, есть ли слэш внутри
            if '/' in permalink:
                result = f'https://www.ravelry.com/{permalink}'
                return result
            else:
                # Просто slug - добавляем полный путь
                result = f'https://www.ravelry.com/patterns/library/{permalink}'
                return result
        
        # Любой другой путь
        else:
            result = f'https://www.ravelry.com{permalink}'
            return result
        
    if ravelry_id:
        try:
            # Пробуем числовой ID
            pattern_id_int = int(ravelry_id)
            result = f'https://www.ravelry.com/patterns/library/{pattern_id_int}'
        except (ValueError, TypeError):
            # ID не число
            result = f'https://www.ravelry.com/patterns/library/{ravelry_id}'
            return result
    
    # Запасной вариант
    result = f'https://www.ravelry.com/patterns/search'
    return result


def save_real_patterns(patterns_data, count):
    """Сохраняет реальные схемы"""
    saved_patterns = []
    
    for i, pattern_data in enumerate(patterns_data[:count], 1):
        try:
            if not isinstance(pattern_data, dict):
                continue
            
            name = pattern_data.get('name', f'Схема {i}')
            ravelry_id_value = pattern_data.get('id')
            
            if not name or not ravelry_id_value:
                continue
            
            # Проверяем, есть ли уже такая схема
            if Pattern.objects.filter(ravelry_id=str(ravelry_id_value)).exists():
                continue
            
            # ОТЛАДКА: покажем permalink
            permalink = pattern_data.get('permalink', '')
            
            # Получаем автора
            designer_data = pattern_data.get('designer', {})
            author = designer_data.get('name', 'Неизвестно') if isinstance(designer_data, dict) else 'Неизвестно'
            
            # Получаем вес пряжи
            yarn_weight_data = pattern_data.get('yarn_weight', {})
            yarn_weight = yarn_weight_data.get('name', '') if isinstance(yarn_weight_data, dict) else ''
            
            # Сложность
            difficulty_rating = pattern_data.get('difficulty_average', 0)
            if difficulty_rating <= 1.5:
                difficulty = 'beginner'
            elif difficulty_rating <= 2.5:
                difficulty = 'easy'
            elif difficulty_rating <= 3.5:
                difficulty = 'intermediate'
            else:
                difficulty = 'experienced'
            
            # Фото
            first_photo = pattern_data.get('first_photo', {})
            if isinstance(first_photo, dict):
                print(f"      Доступные размеры фото:")
                for key, value in first_photo.items():
                    if 'url' in key.lower() and value:
                        print(f"      - {key}: {value[:50]}...")


            photo_url = get_best_photo_url(first_photo)
            
            # Рейтинг
            rating_data = pattern_data.get('rating', {})
            rating = rating_data.get('average', 0) if isinstance(rating_data, dict) else 0

            pattern_url = create_ravelry_url(pattern_data, ravelry_id_value)
            
            # Проверяем наличие слэша после .com
            if 'ravelry.com' in pattern_url and 'ravelry.com/' not in pattern_url:
                # Автоматически исправляем
                if pattern_url.endswith('ravelry.com'):
                    pattern_url = f'{pattern_url}/'
            
            # Создаем схему
            pattern = Pattern.objects.create(
                ravelry_id=str(ravelry_id_value),
                name=name[:200],
                author=author[:200],
                yarn_weight=yarn_weight[:50],
                difficulty=difficulty,
                is_free=pattern_data.get('free', False),
                rating=rating,
                pattern_url=pattern_url,
                photo_url=photo_url,
                craft='knitting',
                source='ravelry'
            )
            
            saved_patterns.append(pattern)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            continue
    
    # Ответ
    response_patterns = []
    for pattern in saved_patterns:
        response_patterns.append({
            'id': pattern.id,
            'name': pattern.name,
            'designer': pattern.author,
            'yarn_weight': pattern.yarn_weight,
            'photo_url': pattern.photo_url,
            'difficulty': pattern.get_difficulty_display(),
            'is_free': pattern.is_free,
            'rating': float(pattern.rating) if pattern.rating else 0,
            'pattern_url': pattern.pattern_url,
        })
    
    message = f'Загружено {len(saved_patterns)} схем' if saved_patterns else 'Нет новых схем'
    
    return JsonResponse({
        'success': True,
        'message': message,
        'patterns': response_patterns,
        'count': len(saved_patterns)
    })

def get_best_photo_url(photo_data):
    """Возвращает URL фото максимального качества"""
    if not isinstance(photo_data, dict):
        return ''
    
    # Порядок приоритета: от лучшего к худшему
    quality_order = [
        'large2_url',    # 1024x1024 (лучшее)
        'large_url',     # 600x600
        'medium2_url',   # 500x500
        'medium_url',    # 300x300 (минимально приемлемое)
        'small_url',     # 150x150 (плохое)
        'square_url',    # 75x75 (очень плохое)
        'thumbnail_url', # миниатюра
    ]
    
    for quality in quality_order:
        url = photo_data.get(quality)
        if url and isinstance(url, str) and url.startswith('http'):
            return url
    
    # Если ничего не нашли
    return ''

def create_test_patterns(count):
    """Создает тестовые схемы"""
    import random
    
    test_patterns = []
    
    yarn_weights = ['Worsted', 'DK', 'Fingering', 'Sport', 'Bulky']
    designers = ['Nora Gaughan', 'Andrea Mowry', 'Stephen West', 'Tin Can Knits']
    pattern_names = ['Cozy Sweater', 'Lace Shawl', 'Cable Hat', 'Colorwork Mittens']
    
    for i in range(1, count + 1):
        try:
            ravelry_id = f"test_{i}_{random.randint(1000, 9999)}"
            
            if Pattern.objects.filter(ravelry_id=ravelry_id).exists():
                continue
            
            name = f'{random.choice(pattern_names)} {i}'
            
            # Создаем тестовый URL для Ravelry
            pattern_url = get_pattern_url_from_ravelry(ravelry_id)
            
            pattern = Pattern.objects.create(
                ravelry_id=ravelry_id,
                name=name,
                author=random.choice(designers),
                yarn_weight=random.choice(yarn_weights),
                difficulty=random.choice(['beginner', 'easy', 'intermediate']),
                is_free=random.choice([True, False]),
                rating=round(random.uniform(3.5, 5.0), 1),
                pattern_url=pattern_url,
                photo_url='',
                craft='knitting',
                source='test'
            )
            
            test_patterns.append({
                'id': pattern.id,
                'name': pattern.name,
                'designer': pattern.author,
                'yarn_weight': pattern.yarn_weight,
                'photo_url': pattern.photo_url,
                'difficulty': pattern.get_difficulty_display(),
                'is_free': pattern.is_free,
                'rating': float(pattern.rating),
                'pattern_url': pattern.pattern_url,
            })
            
        except Exception as e:
            continue
    
    return JsonResponse({
        'success': True,
        'message': f'Создано {len(test_patterns)} тестовых схем',
        'patterns': test_patterns,
        'count': len(test_patterns)
    })

@csrf_exempt
@login_required
def refresh_patterns_simple(request):
    try:
        count = int(request.POST.get('count', 20))
        return create_test_patterns(count)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@login_required
def refresh_patterns_force(request):
    """Перезагрузка всех схем"""
    try:
        count = int(request.POST.get('count', 6))
        
        # Удаляем все схемы
        deleted = Pattern.objects.all().delete()
        
        # Создаем новые
        return create_test_patterns(count)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def load_more_patterns(request):
    """AJAX загрузка дополнительных схем из базы"""
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            offset = int(request.GET.get('offset', 0))
            limit = int(request.GET.get('limit', 5))
            
            # Получаем схемы из базы с пагинацией
            patterns = Pattern.objects.order_by('-created_at')[offset:offset + limit]
            
            patterns_data = []
            for pattern in patterns:
                patterns_data.append({
                    'id': pattern.id,
                    'name': pattern.name,
                    'yarn_weight': pattern.yarn_weight,
                    'photo_url': pattern.photo_url,
                    'difficulty': pattern.get_difficulty_display(),
                    'is_free': pattern.is_free,
                    'rating': pattern.rating,
                    'pattern_url': pattern.pattern_url,
                    'designer': pattern.author,
                })
            
            return JsonResponse({
                'success': True,
                'patterns': patterns_data,
                'count': len(patterns_data),
                'has_more': Pattern.objects.count() > offset + limit
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Неправильный метод запроса'})

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