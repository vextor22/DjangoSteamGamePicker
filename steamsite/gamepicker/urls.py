from django.urls import include, path
from django.contrib import admin

from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('select_game/', views.select_game, name='select_game'),
        ]
