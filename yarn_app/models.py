from django.db import models
from django.contrib.auth.models import User

class UserYarn(models.Model):
    YARN_TYPES = [
        ('fingering', 'Тонкая (Fingering)'),
        ('sport', 'Спортивная (Sport)'),
        ('dk', 'Средняя (DK)'),
        ('worsted', 'Камвольная (Worsted)'),
        ('bulky', 'Толстая (Bulky)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    yarn_type = models.CharField(max_length=20, choices=YARN_TYPES)
    color = models.CharField(max_length=30)
    amount = models.IntegerField()  # в граммах
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.color} {self.get_yarn_type_display()} ({self.amount}г)"


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
