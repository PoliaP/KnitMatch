from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Аутентификация
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Пряжа
    path('yarn/', views.my_yarn, name='my_yarn'),
    path('add-yarn/', views.add_yarn, name='add_yarn'),
    path('yarn/<int:yarn_id>/', views.yarn_detail, name='yarn_detail'),
    path('yarn/<int:yarn_id>/delete/', views.delete_yarn, name='delete_yarn'),
    path('yarn/<int:yarn_id>/projects/', views.yarn_projects, name='yarn_projects'),
    path('yarn/<int:yarn_id>/use/', views.use_in_project, name='use_in_project'),
    
    # Проекты
    path('projects/', views.projects, name='projects'),
    path('projects/add/', views.add_project, name='add_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/delete/<int:project_id>/', views.delete_project, name='delete_project'),
    
    # Схемы и поиск
    path('patterns/', views.pattern_search, name='pattern_search'),
    path('patterns/favorites/', views.favorites, name='favorites'),
    path('patterns/favorite/<int:pattern_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('patterns/load-more/', views.load_more_patterns, name='load_more_patterns'),
    path('patterns/refresh/', views.refresh_patterns, name='refresh_patterns'),
]