from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.interview.models import InterviewSession, InterviewQuestion, CodeSubmission
from django.db.models import Count, Avg
import json

def index(request):
    return render(request, 'core/index.html')

def progress(request):
    """Progress tracking page"""
    context = {
        'total_sessions': 0,
        'technical_sessions': 0,
        'hr_sessions': 0,
        'average_score': 0,
        'recent_sessions': [],
        'skill_breakdown': {}
    }
    
    if request.user.is_authenticated:
        # Get user's interview sessions
        sessions = InterviewSession.objects.filter(user=request.user)
        context['total_sessions'] = sessions.count()
        context['technical_sessions'] = sessions.filter(interview_type='technical').count()
        context['hr_sessions'] = sessions.filter(interview_type='hr').count()
        
        # Calculate average score
        questions = InterviewQuestion.objects.filter(session__user=request.user)
        scores = []
        for q in questions:
            if q.feedback and isinstance(q.feedback, dict) and 'score' in q.feedback:
                scores.append(q.feedback['score'])
        
        if scores:
            context['average_score'] = round(sum(scores) / len(scores), 1)
        
        # Get recent sessions
        context['recent_sessions'] = sessions.order_by('-created_at')[:5]
        
        # Skill breakdown
        context['skill_breakdown'] = {
            'technical': context['technical_sessions'],
            'hr': context['hr_sessions'],
            'coding': CodeSubmission.objects.filter(session__user=request.user).count()
        }
    
    return render(request, 'core/progress.html', context)