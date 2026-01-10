# api_views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
import json
from .models import Pattern, Favorite
from .ravelry_api import RavelryAPI, get_yarn_type_mapping

@require_GET
def api_patterns(request):
    """API endpoint для получения схем с пагинацией и фильтрацией"""
    try:
        # Параметры запроса
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 12))
        difficulty = request.GET.get('difficulty', '')
        yarn_weight = request.GET.get('yarn_weight', '')
        category = request.GET.get('category', '')
        free_only = request.GET.get('free_only', 'false') == 'true'
        search_query = request.GET.get('search', '')
        
        # Сначала проверяем, есть ли схемы в базе
        if not Pattern.objects.exists():
            # Загружаем схемы из Ravelry API если база пуста
            RavelryAPI.fetch_popular_patterns(count=20)
        
        # Базовый QuerySet
        patterns_qs = Pattern.objects.all()
        
        # Применяем фильтры
        if difficulty:
            patterns_qs = patterns_qs.filter(difficulty=difficulty)
        
        if yarn_weight:
            # Преобразуем наш тип пряжи в Ravelry weights
            type_mapping = get_yarn_type_mapping()
            ravelry_weights = type_mapping.get(yarn_weight, [])
            
            # Создаем Q объект для поиска по всем возможным весам
            yarn_q = Q()
            for weight in ravelry_weights:
                yarn_q |= Q(yarn_weight__icontains=weight)
            patterns_qs = patterns_qs.filter(yarn_q)
        
        if category:
            patterns_qs = patterns_qs.filter(category=category)
        
        if free_only:
            patterns_qs = patterns_qs.filter(is_free=True)
        
        if search_query:
            patterns_qs = patterns_qs.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(author__icontains=search_query)
            )
        
        # Сортируем по рейтингу или дате создания
        patterns_qs = patterns_qs.order_by('-rating', '-created_at')
        
        # Пагинация
        paginator = Paginator(patterns_qs, per_page)
        page_obj = paginator.get_page(page)
        
        # Подготавливаем данные для ответа
        patterns_data = []
        for pattern in page_obj:
            patterns_data.append({
                'id': str(pattern.id),
                'name': pattern.name,
                'author': pattern.author or 'Не указан',
                'description': pattern.description or '',
                'difficulty': pattern.difficulty,
                'difficulty_display': pattern.get_difficulty_display(),
                'yarn_weight': pattern.yarn_weight or 'Не указано',
                'category': pattern.category or 'Не указано',
                'craft': 'Спицы' if pattern.craft == 'knitting' else 'Крючок',
                'is_free': pattern.is_free,
                'rating': float(pattern.rating) if pattern.rating else 0,
                'rating_count': pattern.rating_count or 0,
                'photo_url': pattern.photo_url or '/static/images/pattern-placeholder.jpg',
                'pattern_url': pattern.pattern_url or '#',
                'created_at': pattern.created_at.strftime('%d.%m.%Y') if pattern.created_at else ''
            })
        
        response_data = {
            'patterns': patterns_data,
            'page': page,
            'total_pages': paginator.num_pages,
            'total_patterns': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'patterns': []
        }, status=500)

@login_required
@require_POST
@csrf_exempt
def api_favorites(request):
    """API endpoint для работы с избранным"""
    try:
        data = json.loads(request.body)
        pattern_id = data.get('pattern_id')
        action = data.get('action', 'toggle')
        
        if not pattern_id:
            return JsonResponse({'error': 'pattern_id is required'}, status=400)
        
        pattern = Pattern.objects.get(id=pattern_id)
        
        if action == 'add':
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                pattern=pattern
            )
            message = 'Схема добавлена в избранное'
            
        elif action == 'remove':
            Favorite.objects.filter(user=request.user, pattern=pattern).delete()
            message = 'Схема удалена из избранного'
            created = False
            
        else:  # toggle
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                pattern=pattern
            )
            if not created:
                favorite.delete()
                message = 'Схема удалена из избранного'
                created = False
            else:
                message = 'Схема добавлена в избранное'
        
        # Получаем обновленный список избранного
        favorites = list(Favorite.objects.filter(user=request.user).values_list('pattern_id', flat=True))
        
        return JsonResponse({
            'success': True,
            'message': message,
            'is_favorite': created,
            'favorites': favorites,
            'favorites_count': len(favorites)
        })
        
    except Pattern.DoesNotExist:
        return JsonResponse({'error': 'Pattern not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_GET
def api_user_favorites(request):
    """API endpoint для получения избранного пользователя"""
    try:
        favorites = Favorite.objects.filter(user=request.user)
        favorites_data = list(favorites.values_list('pattern_id', flat=True))
        
        return JsonResponse({
            'success': True,
            'favorites': favorites_data,
            'count': len(favorites_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)