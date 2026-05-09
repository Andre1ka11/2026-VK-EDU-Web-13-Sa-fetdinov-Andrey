from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:id>/', views.question_detail, name='question'),
    path('ask/', views.ask, name='ask'),
    path('question/like/', views.question_like, name='question_like'),
    path('answer/like/', views.answer_like, name='answer_like'),
    path('answer/correct/', views.mark_correct, name='mark_correct'),
]
