from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_yarn, name='my_yarn'),
    path('add/', views.add_yarn, name='add_yarn'),
    path('<int:yarn_id>/delete/', views.delete_yarn, name='delete_yarn'),
    path('<int:yarn_id>/', views.yarn_detail, name='yarn_detail'),
]