from django.urls import path
from . import views

app_name = 'dsa'

urlpatterns = [
    path('questions/', views.dsa_questions, name='questions'),
    path('practice/', views.dsa_practice, name='practice'),
    path('solve/<int:question_id>/', views.dsa_solve, name='solve'),
    path('api/question/<int:question_id>/', views.get_question_detail, name='question_detail'),
]