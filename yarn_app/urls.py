from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_yarn, name='my_yarn'),
    path('add/', views.add_yarn, name='add_yarn'),
]