from django.contrib import admin
from .models import DSAQuestion

@admin.register(DSAQuestion)
class DSAQuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'category', 'leetcode_url', 'created_at']
    list_filter = ['difficulty', 'category']
    search_fields = ['title', 'description']
    ordering = ['difficulty', 'title']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'difficulty', 'category')
        }),
        ('Problem Details', {
            'fields': ('examples', 'constraints', 'solution_approach')
        }),
        ('Complexity', {
            'fields': ('time_complexity', 'space_complexity')
        }),
        ('External Links', {
            'fields': ('leetcode_url',)
        }),
    )