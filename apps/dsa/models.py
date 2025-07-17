from django.db import models

class DSAQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    CATEGORY_CHOICES = [
        ('array', 'Arrays'),
        ('string', 'Strings'),
        ('linkedlist', 'Linked Lists'),
        ('tree', 'Trees'),
        ('graph', 'Graphs'),
        ('dp', 'Dynamic Programming'),
        ('sorting', 'Sorting'),
        ('searching', 'Searching'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    examples = models.TextField(blank=True)
    constraints = models.TextField(blank=True)
    solution_approach = models.TextField(blank=True)
    time_complexity = models.CharField(max_length=50, blank=True)
    space_complexity = models.CharField(max_length=50, blank=True)
    leetcode_url = models.URLField(blank=True, help_text="Direct link to the LeetCode problem")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['difficulty', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"