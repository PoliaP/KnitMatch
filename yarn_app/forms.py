from django import forms
from .models import UserYarn

class YarnForm(forms.ModelForm):
    class Meta:
        model = UserYarn
        fields = ['name', 'yarn_type', 'color', 'color_name', 'weight', 
                 'amount', 'manufacturer', 'thickness', 'strength', 
                 'location', 'notes']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Альпака премиум'
            }),
            'yarn_type': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'style': 'height: 40px;'
            }),
            'color_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название цвета'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '100'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Alize, YarnArt'
            }),
            'thickness': forms.Select(attrs={'class': 'form-select'}),
            'strength': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Шкаф, коробка №3'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительная информация...'
            }),
        }