from django.db import models
from django.contrib.auth.models import User

class UserYarn(models.Model):
    YARN_TYPES = [
        ('fingering', 'Тонкая (Fingering)'),
        ('sport', 'Спортивная (Sport)'),
        ('dk', 'Средняя (DK)'),
        ('worsted', 'Камвольная (Worsted)'),
        ('bulky', 'Толстая (Bulky)'),
        ('other', 'Другая'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Название пряжи")
    yarn_type = models.CharField(max_length=20, choices=YARN_TYPES, verbose_name="Тип пряжи")
    color = models.CharField(max_length=30, verbose_name="Цвет")
    amount = models.IntegerField(verbose_name="Количество (мотки)")
    weight = models.IntegerField(verbose_name="Вес (г)", blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True, verbose_name="Производитель")
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_weight(self):
        """Возвращает общий вес всех мотков этой пряжи"""
        if self.weight:
            return self.amount * self.weight
        return 0
    
    def __str__(self):
        if self.name:
            return f"{self.name} - {self.color}"
        return f"{self.color} {self.get_yarn_type_display()}"


class Pattern(models.Model):
    ravelry_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    yarn_weight = models.CharField(max_length=50)
    photo_url = models.URLField(blank=True)
    source = models.CharField(max_length=20, default='ravelry')
    pattern_url = models.URLField(blank=True, verbose_name="Ссылка на схему")
    difficulty = models.CharField(max_length=20, blank=True, 
                                 choices=[('beginner', 'Начинающий'),
                                         ('easy', 'Легкий'),
                                         ('intermediate', 'Средний'),
                                         ('experienced', 'Опытный')])
    craft = models.CharField(max_length=20, default='knitting', 
                            choices=[('knitting', 'Вязание'), 
                                    ('crochet', 'Вязание крючком')])
    is_free = models.BooleanField(default=False, verbose_name="Бесплатная")
    rating = models.FloatField(default=0, verbose_name="Рейтинг")  # Это поле важно!
    rating_count = models.IntegerField(default=0, verbose_name="Количество оценок")
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=200, blank=True, null=True, verbose_name="Автор")
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="Категория")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    
    class Meta:
        ordering = ['-rating']
    
    def __str__(self):
        return self.name
    
    @property
    def difficulty_display(self):
        difficulty_dict = {
            'beginner': 'Начинающий',
            'easy': 'Легкий',
            'intermediate': 'Средний',
            'experienced': 'Опытный'
        }
        return difficulty_dict.get(self.difficulty, 'Не указано')
    
    @property
    def difficulty_stars(self):
        """Возвращает количество звезд сложности"""
        mapping = {
            'beginner': 1,
            'easy': 2,
            'intermediate': 3,
            'experienced': 4
        }
        return mapping.get(self.difficulty, 1)


class Project(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Запланирован'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
        ('frogged', 'Распущен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name="Название проекта")
    pattern = models.ForeignKey(Pattern, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    description = models.TextField(blank=True, verbose_name="Описание")
    start_date = models.DateField(null=True, blank=True, verbose_name="Дата начала")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата завершения")
    progress = models.IntegerField(default=0, verbose_name="Прогресс (%)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class ProjectYarn(models.Model):
    """Связь проекта с используемой пряжей"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_yarns')
    user_yarn = models.ForeignKey(UserYarn, on_delete=models.CASCADE)
    amount_used = models.IntegerField(verbose_name="Использовано мотков")
    notes = models.TextField(blank=True, verbose_name="Примечания по использованию")
    
    class Meta:
        unique_together = ['project', 'user_yarn']


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pattern = models.ForeignKey('Pattern', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'pattern']
    
    def __str__(self):
        return f"{self.user.username} - {self.pattern.name}"