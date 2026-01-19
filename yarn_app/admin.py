from django.contrib import admin
from django.db.models import Count, Sum, Avg
from django.utils.html import format_html
from .models import UserYarn, Pattern, Project, ProjectYarn, Favorite
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# ==================== INLINE МОДЕЛИ ====================

class UserYarnInline(admin.TabularInline):
    """Inline отображение пряжи пользователя"""
    model = UserYarn
    extra = 0
    fields = ('name', 'yarn_type', 'color', 'amount', 'total_weight_display')
    readonly_fields = ('total_weight_display',)
    
    def total_weight_display(self, obj):
        if obj.total_weight:
            return f"{obj.total_weight} г"
        return "не указан"
    total_weight_display.short_description = "Общий вес"

class FavoriteInline(admin.TabularInline):
    """Inline отображение избранного пользователя"""
    model = Favorite
    extra = 0
    fields = ('pattern', 'added_at')
    readonly_fields = ('added_at',)
    raw_id_fields = ('pattern',)

class ProjectInline(admin.TabularInline):
    """Inline отображение проектов пользователя"""
    model = Project
    extra = 0
    fields = ('name', 'status', 'progress', 'start_date')
    readonly_fields = ('progress',)

# ==================== АДМИНКИ МОДЕЛЕЙ ====================

@admin.register(UserYarn)
class UserYarnAdmin(admin.ModelAdmin):
    list_display = ('id', 'colored_name', 'user', 'yarn_type_display', 'colored_color', 
                    'amount_with_icon', 'weight_display', 'total_weight_display', 'created_at')
    list_filter = ('yarn_type', 'created_at', 'user')
    search_fields = ('name', 'color', 'manufacturer', 'user__username')
    list_editable = ('amount',)
    list_per_page = 25
    ordering = ('-created_at',)
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'yarn_type', 'color')
        }),
        ('Количество и вес', {
            'fields': ('amount', 'weight')
        }),
        ('Дополнительно', {
            'fields': ('manufacturer', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'total_weight')
    
    # Кастомные методы для отображения
    def yarn_type_display(self, obj):
        return obj.get_yarn_type_display()
    yarn_type_display.short_description = 'Тип пряжи'
    
    def colored_name(self, obj):
        if obj.name:
            return format_html('<b>{}</b>', obj.name)
        return format_html('<i>Без названия</i>')
    colored_name.short_description = 'Название'
    
    def colored_color(self, obj):
        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<div style="width: 20px; height: 20px; background-color: {}; '
            'border-radius: 3px; margin-right: 8px; border: 1px solid #ddd;"></div>'
            '<span>{}</span>'
            '</div>',
            obj.color, obj.color
        )
    colored_color.short_description = 'Цвет'
    
    def amount_with_icon(self, obj):
        icon = '🧶' if obj.amount > 0 else '⚪'
        return format_html('{} {} мот.', icon, obj.amount)
    amount_with_icon.short_description = 'Количество'
    
    def weight_display(self, obj):
        if obj.weight:
            return f"{obj.weight} г"
        return "—"
    weight_display.short_description = 'Вес мотка'
    
    def total_weight_display(self, obj):
        if obj.total_weight:
            return format_html('<b>{} г</b>', obj.total_weight)
        return "—"
    total_weight_display.short_description = 'Общий вес'
    
    # Действия в админке
    actions = ['duplicate_yarn', 'calculate_total_weight']
    
    def duplicate_yarn(self, request, queryset):
        """Дублировать выбранную пряжу"""
        count = 0
        for yarn in queryset:
            yarn.pk = None
            yarn.name = f"{yarn.name} (копия)" if yarn.name else "Копия пряжи"
            yarn.save()
            count += 1
        self.message_user(request, f"Создано {count} копий пряжи")
    duplicate_yarn.short_description = "Дублировать пряжу"
    
    def calculate_total_weight(self, request, queryset):
        """Рассчитать общий вес для выбранной пряжи"""
        total = sum(yarn.total_weight for yarn in queryset if yarn.total_weight)
        self.message_user(request, f"Общий вес выбранной пряжи: {total} г")
    calculate_total_weight.short_description = "Рассчитать общий вес"

@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_with_link', 'author', 'difficulty_stars_display', 
                    'rating_bar', 'is_free_display', 'yarn_weight', 'created_at')
    list_filter = ('difficulty', 'is_free', 'yarn_weight', 'craft', 'created_at')
    search_fields = ('name', 'author', 'description', 'category')
    list_per_page = 30
    ordering = ('-rating',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'author', 'description', 'category')
        }),
        ('Технические данные', {
            'fields': ('difficulty', 'yarn_weight', 'craft', 'yardage', 'rating', 'rating_count')
        }),
        ('Ссылки и метаданные', {
            'fields': ('pattern_url', 'photo_url', 'is_free', 'published'),
            'classes': ('collapse',)
        }),
        ('Ravelry данные', {
            'fields': ('ravelry_id', 'source'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'ravelry_id')
    
    def name_with_link(self, obj):
        if obj.pattern_url:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                obj.pattern_url, obj.name
            )
        return obj.name
    name_with_link.short_description = 'Название'
    
    def difficulty_stars_display(self, obj):
        stars = obj.difficulty_stars
        filled_stars = '★' * stars
        empty_stars = '☆' * (4 - stars)
        color = {
            1: 'green',
            2: 'lightgreen',
            3: 'orange',
            4: 'red'
        }.get(stars, 'gray')
        return format_html(
            '<span style="color: {};" title="{}">{}{}</span>',
            color, obj.difficulty_display, filled_stars, empty_stars
        )
    difficulty_stars_display.short_description = 'Сложность'
    
    def rating_bar(self, obj):
        if obj.rating > 0:
            width = min(obj.rating * 20, 100)  # 5 звезд = 100%
            color = 'gold' if obj.rating >= 4 else 'orange' if obj.rating >= 3 else 'lightblue'
            return format_html(
                '<div style="width: 100px; background: #eee; border-radius: 3px; overflow: hidden;">'
                '<div style="width: {}%; height: 20px; background: {}; text-align: center; '
                'color: black; font-weight: bold; line-height: 20px;">{:.1f}</div>'
                '</div>',
                width, color, obj.rating
            )
        return "—"
    rating_bar.short_description = 'Рейтинг'
    
    def is_free_display(self, obj):
        if obj.is_free:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Бесплатно</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">💰 Платно</span>'
        )
    is_free_display.short_description = 'Бесплатная'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_with_status', 'user', 'pattern_link', 
                    'progress_bar', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'start_date', 'created_at', 'user')
    search_fields = ('name', 'description', 'user__username')
    list_per_page = 25
    ordering = ('-created_at',)
    raw_id_fields = ('user', 'pattern')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'pattern', 'description', 'status')
        }),
        ('Даты и прогресс', {
            'fields': ('start_date', 'end_date', 'progress')
        }),
    )
    
    readonly_fields = ('created_at',)
    inlines = []  # Можно добавить ProjectYarnInline
    
    def name_with_status(self, obj):
        status_colors = {
            'planned': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'frogged': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<b>{}</b> <span style="color: {};">({})</span>',
            obj.name, color, obj.get_status_display()
        )
    name_with_status.short_description = 'Проект'
    
    def pattern_link(self, obj):
        if obj.pattern:
            return format_html(
                '<a href="../pattern/{}/">{}</a>',
                obj.pattern.id, obj.pattern.name[:50]
            )
        return "—"
    pattern_link.short_description = 'Схема'
    
    def progress_bar(self, obj):
        color = 'green' if obj.progress >= 100 else 'orange' if obj.progress >= 50 else 'lightblue'
        return format_html(
            '<div style="width: 80px; background: #eee; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; height: 20px; background: {}; text-align: center; '
            'color: white; font-weight: bold; line-height: 20px;">{}%</div>'
            '</div>',
            obj.progress, color, obj.progress
        )
    progress_bar.short_description = 'Прогресс'

@admin.register(ProjectYarn)
class ProjectYarnAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_link', 'yarn_link', 'amount_used', 'notes_preview')
    list_filter = ('project__status', 'project__user')
    search_fields = ('project__name', 'user_yarn__name', 'notes')
    list_per_page = 25
    raw_id_fields = ('project', 'user_yarn')
    
    def project_link(self, obj):
        return format_html(
            '<a href="../project/{}/">{}</a>',
            obj.project.id, obj.project.name
        )
    project_link.short_description = 'Проект'
    
    def yarn_link(self, obj):
        yarn = obj.user_yarn
        yarn_name = yarn.name if yarn.name else f"{yarn.color} {yarn.get_yarn_type_display()}"
        return format_html(
            '<a href="../useryarn/{}/">{}</a>',
            yarn.id, yarn_name
        )
    yarn_link.short_description = 'Пряжа'
    
    def notes_preview(self, obj):
        if obj.notes and len(obj.notes) > 50:
            return f"{obj.notes[:50]}..."
        return obj.notes or "—"
    notes_preview.short_description = 'Примечания'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'pattern_link', 'added_at')
    list_filter = ('added_at', 'user')
    search_fields = ('user__username', 'pattern__name')
    list_per_page = 30
    ordering = ('-added_at',)
    raw_id_fields = ('user', 'pattern')
    
    def user_link(self, obj):
        return format_html(
            '<a href="../user/{}/">{}</a>',
            obj.user.id, obj.user.username
        )
    user_link.short_description = 'Пользователь'
    
    def pattern_link(self, obj):
        return format_html(
            '<a href="../pattern/{}/">{}</a>',
            obj.pattern.id, obj.pattern.name[:100]
        )
    pattern_link.short_description = 'Схема'

# ==================== КАСТОМИЗАЦИЯ АДМИНКИ ПОЛЬЗОВАТЕЛЕЙ ====================

class CustomUserAdmin(BaseUserAdmin):
    """Расширенная админка для пользователей"""
    inlines = [UserYarnInline, FavoriteInline, ProjectInline]
    list_display = ('username', 'email', 'date_joined', 'is_staff', 
                    'yarn_count', 'favorite_count', 'project_count')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('KnitMatch Статистика', {
            'fields': ('yarn_count', 'favorite_count', 'project_count'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('yarn_count', 'favorite_count', 'project_count')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _yarn_count=Count('useryarn', distinct=True),
            _favorite_count=Count('favorite', distinct=True),
            _project_count=Count('project', distinct=True)
        )
        return queryset
    
    def yarn_count(self, obj):
        return getattr(obj, '_yarn_count', 0)
    yarn_count.short_description = 'Пряжи'
    
    def favorite_count(self, obj):
        return getattr(obj, '_favorite_count', 0)
    favorite_count.short_description = 'Избранного'
    
    def project_count(self, obj):
        return getattr(obj, '_project_count', 0)
    project_count.short_description = 'Проектов'

# Перерегистрируем стандартную админку пользователей
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ==================== КАСТОМИЗАЦИЯ ГЛАВНОЙ СТРАНИЦЫ АДМИНКИ ====================

class CustomAdminSite(admin.AdminSite):
    site_header = "🧶 Администрирование KnitMatch"
    site_title = "KnitMatch Admin"
    index_title = "Панель управления вязальным сообществом"
    
    def index(self, request, extra_context=None):
        """Кастомизация главной страницы админки"""
        extra_context = extra_context or {}
        
        # Статистика для дашборда
        from django.db.models import Count, Sum
        
        # Общая статистика
        extra_context['total_users'] = User.objects.count()
        extra_context['total_yarn'] = UserYarn.objects.count()
        extra_context['total_patterns'] = Pattern.objects.count()
        extra_context['total_favorites'] = Favorite.objects.count()
        extra_context['total_projects'] = Project.objects.count()
        
        # Статистика по пряже
        yarn_stats = UserYarn.objects.aggregate(
            total_amount=Sum('amount'),
            avg_weight=Avg('weight'),
            total_weight=Sum('amount') * Avg('weight')
        )
        extra_context.update(yarn_stats)
        
        # Топ пользователей
        extra_context['top_users'] = User.objects.annotate(
            yarn_count=Count('useryarn')
        ).order_by('-yarn_count')[:5]
        
        return super().index(request, extra_context)
