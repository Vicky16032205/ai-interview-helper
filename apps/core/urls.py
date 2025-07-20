from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('progress/', views.progress, name='progress'),
    path('submit-review/', views.submit_review, name='submit_review'),
]