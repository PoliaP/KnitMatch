"""
URL configuration for knitmatch_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib.auth import views as auth_views
from yarn_app import views as yarn_views

urlpatterns = [
    # Главная страница
    path('', yarn_views.home, name='home'),
    
    # Аутентификация
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('signup/', yarn_views.signup, name='signup'),
    
    # Приложение yarn_app (только для операций с пряжей)
    path('yarn/', include('yarn_app.urls')),
    
    # Проекты (отдельно, чтобы избежать конфликтов)
    path('projects/', yarn_views.projects, name='projects'),
    path('projects/add/', yarn_views.add_project, name='add_project'),
    path('projects/<int:project_id>/', yarn_views.project_detail, name='project_detail'),
    path('projects/delete/<int:project_id>/', yarn_views.delete_project, name='delete_project'),
    
    # Схемы и поиск
    path('patterns/', yarn_views.pattern_search, name='pattern_search'),
    path('patterns/favorites/', yarn_views.favorites, name='favorites'),
    path('patterns/favorite/<int:pattern_id>/', yarn_views.toggle_favorite, name='toggle_favorite'),
    path('patterns/load-more/', yarn_views.load_more_patterns, name='load_more_patterns'),
    path('patterns/refresh/', yarn_views.refresh_patterns, name='refresh_patterns'),
]