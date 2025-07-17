from django.contrib import admin
from .models import DSAQuestion

@admin.register(DSAQuestion)
class DSAQuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'category', 'created_at']
    list_filter = ['difficulty', 'category']
    search_fields = ['title', 'description']
    ordering = ['difficulty', 'title']