from django.contrib import admin
from django.utils.html import format_html
from .models import UserYarn, Pattern, Project, ProjectYarn, Favorite


@admin.register(UserYarn)
class UserYarnAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'get_yarn_type_display', 
                    'color_display', 'amount', 'weight', 'created_at_short')
    list_filter = ('yarn_type', 'created_at', 'user')
    search_fields = ('name', 'color', 'manufacturer', 'user__username')
    list_per_page = 25
    ordering = ('-created_at',)
    
    def color_display(self, obj):
        return format_html(
            '<div style="background-color: {}; width: 20px; height: 20px; '
            'border-radius: 3px; border: 1px solid #ddd;"></div>',
            obj.color
        )
    color_display.short_description = 'Цвет'
    
    def created_at_short(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    created_at_short.short_description = 'Добавлено'


@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'difficulty', 
                    'rating', 'is_free', 'yarn_weight', 'created_at_short')
    list_filter = ('difficulty', 'is_free', 'yarn_weight', 'craft')
    search_fields = ('name', 'author', 'description', 'category')
    list_per_page = 30
    ordering = ('-rating',)
    
    def created_at_short(self, obj):
        return obj.created_at.strftime('%d.%m.%Y')
    created_at_short.short_description = 'Добавлено'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'get_status_display', 
                    'progress_display', 'start_date', 'created_at_short')
    list_filter = ('status', 'start_date', 'user')
    search_fields = ('name', 'description', 'user__username')
    list_per_page = 25
    
    def progress_display(self, obj):
        color = 'green' if obj.progress >= 100 else 'orange' if obj.progress >= 50 else 'lightblue'
        return format_html(
            '<div style="width: 60px; background: #eee; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; height: 20px; background: {}; text-align: center; '
            'color: white; font-weight: bold; line-height: 20px;">{}%</div>'
            '</div>',
            obj.progress, color, obj.progress
        )
    progress_display.short_description = 'Прогресс'
    
    def created_at_short(self, obj):
        return obj.created_at.strftime('%d.%m.%Y')
    created_at_short.short_description = 'Создан'


@admin.register(ProjectYarn)
class ProjectYarnAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'user_yarn', 'amount_used', 'notes_preview')
    list_filter = ('project__status', 'project__user')
    search_fields = ('project__name', 'user_yarn__name', 'notes')
    list_per_page = 25
    
    def notes_preview(self, obj):
        if obj.notes and len(obj.notes) > 30:
            return f"{obj.notes[:30]}..."
        return obj.notes or "—"
    notes_preview.short_description = 'Примечания'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pattern', 'added_at_short')
    list_filter = ('added_at', 'user')
    search_fields = ('user__username', 'pattern__name')
    list_per_page = 30
    
    def added_at_short(self, obj):
        return obj.added_at.strftime('%d.%m.%Y %H:%M')
    added_at_short.short_description = 'Добавлено'