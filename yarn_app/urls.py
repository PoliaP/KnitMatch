from django.urls import path
from . import views

urlpatterns = [
    # Главная страница пряжи
    path('', views.my_yarn, name='my_yarn'),
    
    # Операции с пряжей
    path('add/', views.add_yarn, name='add_yarn'),
    path('delete/<int:yarn_id>/', views.delete_yarn, name='delete_yarn'),
    path('<int:yarn_id>/', views.yarn_detail, name='yarn_detail'),
    path('<int:yarn_id>/projects/', views.yarn_projects, name='yarn_projects'),
    
    # Использование пряжи в проекте
    path('<int:yarn_id>/use/', views.use_in_project, name='use_in_project'),
]