from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib import messages
import json
from .models import InterviewSession, InterviewQuestion, CodeSubmission, ResumeAnalysis
from .utils import (
    analyze_code, analyze_technical_answer, analyze_hr_answer,
    analyze_resume, get_technical_questions, get_hr_questions,
    generate_follow_up_question
)

def technical_interview(request):
    """Technical interview page"""
    questions = get_technical_questions()
    context = {
        'questions': questions,
        'difficulties': ['easy', 'medium', 'hard']
    }
    return render(request, 'interview/technical_interview.html', context)

def hr_interview(request):
    """HR interview page"""
    questions = get_hr_questions()
    context = {
        'questions': questions
    }
    return render(request, 'interview/hr_interview.html', context)

@csrf_exempt
def analyze_code_view(request):
    """API endpoint to analyze code"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            language = data.get('language', 'python')
            
            # Create session and submission
            session = InterviewSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
                interview_type='technical'
            )
            
            submission = CodeSubmission.objects.create(
                session=session,
                code=code,
                language=language
            )
            
            # Analyze code
            feedback = analyze_code(code, language)
            submission.feedback = feedback
            submission.save()
            
            return JsonResponse({
                'success': True,
                'feedback': feedback
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def analyze_answer_view(request):
    """API endpoint to analyze interview answer"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '')
            answer = data.get('answer', '')
            interview_type = data.get('type', 'technical')
            is_audio = data.get('is_audio', False)
            
            # Create session and question
            session = InterviewSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
                interview_type=interview_type
            )
            
            question_obj = InterviewQuestion.objects.create(
                session=session,
                question=question,
                answer=answer
            )
            
            # Analyze answer
            if interview_type == 'technical':
                feedback = analyze_technical_answer(question, answer, is_audio)
            else:
                feedback = analyze_hr_answer(question, answer, is_audio)
            
            question_obj.feedback = feedback
            question_obj.save()
            
            # Generate follow-up for HR interviews
            follow_up = None
            if interview_type == 'hr':
                follow_up = generate_follow_up_question(question, answer)
            
            return JsonResponse({
                'success': True,
                'feedback': feedback,
                'follow_up': follow_up
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def upload_resume_view(request):
    """API endpoint to upload and analyze resume"""
    if request.method == 'POST' and request.FILES.get('resume'):
        try:
            resume_file = request.FILES['resume']
            
            # Validate file type
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
            file_extension = resume_file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid file type. Please upload PDF, DOC, DOCX, or TXT files only.'
                }, status=400)
            
            # Validate file size (max 10MB)
            if resume_file.size > 10 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'error': 'File too large. Please upload files smaller than 10MB.'
                }, status=400)
            
            # Save file
            import os
            import uuid
            unique_filename = f"{uuid.uuid4()}_{resume_file.name}"
            file_path = default_storage.save(f'resumes/{unique_filename}', resume_file)
            full_path = default_storage.path(file_path)
            
            # Create resume analysis record
            analysis = ResumeAnalysis.objects.create(
                user=request.user if request.user.is_authenticated else None,
                resume_file=file_path
            )
            
            # Analyze resume using Gemini AI
            feedback = analyze_resume(full_path, file_extension)
            
            analysis.analysis_result = feedback
            analysis.save()
            
            # Clean up the uploaded file after analysis
            try:
                os.remove(full_path)
            except:
                pass  # File cleanup is not critical
            
            return JsonResponse({
                'success': True,
                'feedback': feedback,
                'message': 'Resume analyzed successfully!'
            })
            
        except Exception as e:
            print(f"Resume upload error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while analyzing your resume. Please try again.'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'No resume file provided. Please select a file to upload.'
    }, status=400)

@csrf_exempt
def generate_resume_questions_view(request):
    """API endpoint to generate questions based on resume content"""
    if request.method == 'POST' and request.FILES.get('resume'):
        try:
            resume_file = request.FILES['resume']
            difficulty = request.POST.get('difficulty', 'medium')
            
            # Validate file type
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
            file_extension = resume_file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid file type. Please upload PDF, DOC, DOCX, or TXT files only.'
                }, status=400)
            
            # Save file temporarily
            import os
            import uuid
            unique_filename = f"{uuid.uuid4()}_{resume_file.name}"
            file_path = default_storage.save(f'temp_resumes/{unique_filename}', resume_file)
            full_path = default_storage.path(file_path)
            
            # Generate questions based on resume
            from .utils import generate_questions_from_resume
            questions = generate_questions_from_resume(full_path, file_extension, difficulty)
            
            # Clean up the uploaded file
            try:
                os.remove(full_path)
            except:
                pass
            
            return JsonResponse({
                'success': True,
                'questions': questions,
                'message': 'Questions generated successfully based on your resume!'
            })
            
        except Exception as e:
            print(f"Question generation error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while generating questions. Please try again.'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'No resume file provided. Please select a file to upload.'
    }, status=400)

@csrf_exempt
def save_audio_answer_view(request):
    """API endpoint to save audio answer"""
    if request.method == 'POST' and request.FILES.get('audio'):
        try:
            audio_file = request.FILES['audio']
            question = request.POST.get('question', '')
            interview_type = request.POST.get('type', 'technical')
            
            # Save audio file
            file_path = default_storage.save(f'audio_answers/{audio_file.name}', audio_file)
            
            # Create session and question
            session = InterviewSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
                interview_type=interview_type
            )
            
            question_obj = InterviewQuestion.objects.create(
                session=session,
                question=question,
                audio_answer=file_path
            )
            
            # Here you would transcribe audio and analyze
            # For now, returning mock feedback
            feedback = {
                'score': 8,
                'transcription': 'Audio transcription would go here',
                'feedback': 'Good answer with clear communication'
            }
            
            question_obj.feedback = feedback
            question_obj.save()
            
            return JsonResponse({
                'success': True,
                'feedback': feedback
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)