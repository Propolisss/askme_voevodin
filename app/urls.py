from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('question/<int:question_id>', views.question, name='question'),
    path('tag/<str:given_tag>', views.tag, name='tag'),
    path('ask', views.ask, name='ask'),
    path('settings', views.settings, name='settings'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('hot', views.hot, name='hot'),
    path('logout', views.logout, name='logout'),
]
