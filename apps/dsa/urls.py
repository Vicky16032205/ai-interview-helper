from django.urls import path
from . import views

app_name = 'dsa'

urlpatterns = [
    path('questions/', views.dsa_questions, name='questions'),
    path('practice/', views.dsa_practice, name='practice'),
    path('solve/<int:question_id>/', views.dsa_solve, name='solve'),
    path('api/question/<int:question_id>/', views.get_question_detail, name='question_detail'),
    path('api/generate-question/', views.generate_dynamic_question, name='generate_question'),
    path('api/generate-batch-questions/', views.generate_batch_questions, name='generate_batch_questions'),
    path('api/adaptive-question/', views.generate_adaptive_question, name='adaptive_question'),
]