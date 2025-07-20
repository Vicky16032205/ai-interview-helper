from django.db import models
from django.contrib.auth.models import User

class InterviewSession(models.Model):
    INTERVIEW_TYPES = [
        ('technical', 'Technical'),
        ('hr', 'HR'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

class InterviewQuestion(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    answer = models.TextField(blank=True)
    audio_answer = models.FileField(upload_to='audio_answers/', null=True, blank=True)
    feedback = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

class CodeSubmission(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='code_submissions')
    code = models.TextField()
    language = models.CharField(max_length=50, default='python')
    feedback = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ResumeAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    analysis_result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TechnicalInterviewReport(models.Model):
    """Model to store comprehensive technical interview reports"""
    
    PERFORMANCE_LEVELS = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('satisfactory', 'Satisfactory'),
        ('needs_improvement', 'Needs Improvement'),
    ]
    
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Basic session info
    questions_data = models.JSONField()  # Store all questions
    answers_data = models.JSONField()    # Store all answers
    duration = models.IntegerField()     # Duration in seconds
    
    # Scoring
    overall_score = models.IntegerField()
    performance_level = models.CharField(max_length=20, choices=PERFORMANCE_LEVELS)
    
    # Analysis results
    strengths = models.JSONField()           # List of strengths
    improvements = models.JSONField()        # Areas for improvement
    skill_scores = models.JSONField()        # Technical skill assessments
    question_reviews = models.JSONField()    # Individual question feedback
    recommendations = models.JSONField()     # Personalized recommendations
    
    # Statistics
    questions_answered = models.IntegerField()
    average_answer_length = models.IntegerField()
    voice_answers_count = models.IntegerField()
    text_answers_count = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report {self.session_id} - {self.overall_score}%"
    
    @property
    def formatted_duration(self):
        """Return duration in MM:SS format"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"