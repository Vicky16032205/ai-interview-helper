from django.urls import path
from . import views
from .health_check import health_check

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('progress/', views.progress, name='progress'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('health/', health_check, name='health_check'),
]