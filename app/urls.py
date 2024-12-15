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
    path('question-like/<int:question_id>', views.question_like, name='question-like'),
    path('answer-like/<int:answer_id>', views.answer_like, name='answer-like'),
    path('answer/<int:answer_id>', views.mark_answer, name='mark-answer')
]
