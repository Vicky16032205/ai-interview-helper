from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from apps.interview.models import InterviewSession, InterviewQuestion
from django.db.models import Count, Avg
import json
from datetime import datetime

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
            'hr': context['hr_sessions']
        }
    
    return render(request, 'core/progress.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def submit_review(request):
    """Handle user review submission and send email"""
    try:
        print("=== Review Submission Debug ===")
        print(f"Request method: {request.method}")
        print(f"Request data: {request.POST}")
        
        reviewer_name = request.POST.get('reviewer_name', '')
        reviewer_email = request.POST.get('reviewer_email', '')
        rating = request.POST.get('rating', '5')
        review_message = request.POST.get('review_message', '')
        
        print(f"Extracted data: name={reviewer_name}, email={reviewer_email}, rating={rating}")
        
        # Validate required fields
        if not all([reviewer_name, reviewer_email, review_message]):
            print("Validation failed: missing required fields")
            return JsonResponse({
                'success': False,
                'message': 'All fields are required.'
            })
        
        # Prepare email content
        stars = '⭐' * int(rating)
        subject = f"New Review from {reviewer_name} - AI Interview Helper"
        
        email_body = f"""
🌟 NEW USER REVIEW 🌟

From: {reviewer_name}
Email: {reviewer_email}
Rating: {stars} ({rating}/5)
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Review Message:
{review_message}

---
Sent from AI Interview Helper Review System
        """
        
        print("About to send email...")
        
        # Send email
        try:
            from django.core.mail import get_connection
            from django.conf import settings
            
            # Force SMTP connection for review emails
            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host='smtp.gmail.com',
                port=587,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=True,
            )
            
            result = send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.EMAIL_HOST_USER,  # Must match the authenticated Gmail account
                recipient_list=['vickyguptagkp55@gmail.com'],
                fail_silently=False,
                connection=connection,
            )
            
            print(f"Email sent successfully! Result: {result}")
            
            return JsonResponse({
                'success': True,
                'message': 'Review sent successfully!'
            })
            
        except Exception as email_error:
            print(f"Email sending error: {email_error}")
            print(f"Error type: {type(email_error).__name__}")
            return JsonResponse({
                'success': False,
                'message': f'Failed to send email: {str(email_error)}'
            })
            
    except Exception as e:
        print(f"Review submission error: {e}")
        print(f"Error type: {type(e).__name__}")
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        })