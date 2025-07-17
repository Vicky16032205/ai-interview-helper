from django.urls import path
from . import views

app_name = 'interview'

urlpatterns = [
    path('technical/', views.technical_interview, name='technical'),
    path('hr/', views.hr_interview, name='hr'),
    path('api/analyze-code/', views.analyze_code_view, name='analyze_code'),
    path('api/analyze-answer/', views.analyze_answer_view, name='analyze_answer'),
    path('api/upload-resume/', views.upload_resume_view, name='upload_resume'),
    path('api/save-audio/', views.save_audio_answer_view, name='save_audio'),
]