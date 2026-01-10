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
    
    def __str__(self):
        if self.name:
            return f"{self.name} - {self.color}"
        return f"{self.color} {self.get_yarn_type_display()}"


class Pattern(models.Model):
    ravelry_id = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    yarn_weight = models.CharField(max_length=50)
    photo_url = models.URLField(blank=True)
    source = models.CharField(max_length=20, default='ravelry')
    
    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'pattern']