from django.urls import path
from . import views

app_name = 'interview'

urlpatterns = [
    path('technical/', views.technical_interview, name='technical'),
    path('hr/', views.hr_interview, name='hr'),
    path('api/analyze-answer/', views.analyze_answer_view, name='analyze_answer'),
    path('api/upload-resume/', views.upload_resume_view, name='api_upload_resume'),
    path('api/generate-questions/', views.generate_resume_questions_view, name='api_generate_questions'),
    path('api/save-audio/', views.save_audio_answer_view, name='save_audio'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('generate-questions/', views.generate_interview_questions, name='generate_questions'),
    path('interview-session/', views.interview_session, name='interview_session'),
    path('generate-report/', views.generate_report, name='generate_report'),
    path('report/<str:report_id>/', views.interview_report, name='interview_report'),
]