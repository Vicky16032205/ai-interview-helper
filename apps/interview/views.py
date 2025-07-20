from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
import json
import os
import uuid
from .models import InterviewSession, InterviewQuestion, ResumeAnalysis, TechnicalInterviewReport
from .utils import (
    analyze_technical_answer, analyze_hr_answer,
    analyze_resume, get_technical_questions, get_hr_questions,
    generate_follow_up_question, extract_text_from_file, 
    analyze_resume_with_gemini, generate_technical_questions,
    transcribe_audio, analyze_interview_performance
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
            
            # Save audio file temporarily
            unique_filename = f"{uuid.uuid4()}_{audio_file.name}"
            file_path = default_storage.save(f'audio_answers/{unique_filename}', audio_file)
            full_path = default_storage.path(file_path)
            
            # Transcribe the audio using AssemblyAI (with Google fallback)
            print(f"Transcribing audio file: {full_path}")
            transcribed_text = transcribe_audio(full_path)
            print(f"Transcription result: {transcribed_text}")
            
            # Create session and question
            session = InterviewSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
                interview_type=interview_type
            )
            
            question_obj = InterviewQuestion.objects.create(
                session=session,
                question=question,
                answer=transcribed_text,  # Store the transcribed text as the answer
                audio_answer=file_path
            )
            
            # Analyze the transcribed answer using AI
            if interview_type == 'technical':
                feedback = analyze_technical_answer(question, transcribed_text, is_audio=True)
            else:
                feedback = analyze_hr_answer(question, transcribed_text, is_audio=True)
            
            # Add transcription to feedback for user reference
            feedback['transcription'] = transcribed_text
            
            question_obj.feedback = feedback
            question_obj.save()
            
            # Generate follow-up for HR interviews
            follow_up = None
            if interview_type == 'hr':
                follow_up = generate_follow_up_question(question, transcribed_text)
            
            # Clean up the temporary audio file
            try:
                os.remove(full_path)
            except:
                pass  # File cleanup is not critical
            
            return JsonResponse({
                'success': True,
                'feedback': feedback,
                'follow_up': follow_up,
                'transcription': transcribed_text
            })
            
        except Exception as e:
            print(f"Audio processing error: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error processing audio: {str(e)}'
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
@csrf_exempt
@require_http_methods(["POST"])
def upload_resume(request):
    """Handle resume upload and analysis"""
    try:
        if 'resume' not in request.FILES:
            return JsonResponse({'error': 'No resume file provided'}, status=400)
        
        resume_file = request.FILES['resume']
        
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        file_extension = resume_file.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': 'Invalid file type. Please upload PDF, DOC, DOCX, or TXT files only.'
            }, status=400)
        
        # Save file temporarily to extract text
        unique_filename = f"{uuid.uuid4()}_{resume_file.name}"
        file_path = default_storage.save(f'temp_resumes/{unique_filename}', resume_file)
        full_path = default_storage.path(file_path)
        
        # Extract text from file
        resume_text = extract_text_from_file(full_path, file_extension)
        
        # Clean up the temporary file
        try:
            os.remove(full_path)
        except:
            pass  # File cleanup is not critical
        
        # Analyze with Gemini
        analysis = analyze_resume_with_gemini(resume_text)
        
        # Store in session for later use
        request.session['resume_analysis'] = analysis
        request.session['resume_text'] = resume_text
        
        return JsonResponse({
            'success': True,
            'analysis': analysis,
            'message': 'Resume analyzed successfully'
        })
        
    except Exception as e:
        print(f"Resume upload error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_interview_questions(request):
    """Generate technical interview questions"""
    try:
        data = json.loads(request.body)
        skills = data.get('skills', [])
        experience_level = data.get('experience_level', 'Mid')
        question_count = data.get('count', 10)  # Default to 10 questions for full interview
        
        # Generate questions
        questions = generate_technical_questions(skills, experience_level, question_count)
        
        # Store in session
        request.session['interview_questions'] = questions
        
        return JsonResponse({
            'success': True,
            'questions': questions
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def interview_session(request):
    """Render the full interview session page"""
    questions = request.session.get('interview_questions', [])
    
    if not questions:
        # Redirect back to technical interview page if no questions
        return redirect('interview:technical')
    
    return render(request, 'interview/interview_session.html', {
        'questions': questions
    })

@csrf_exempt
@require_http_methods(["POST"])
def generate_report(request):
    """Generate comprehensive interview report"""
    try:
        data = json.loads(request.body)
        
        # Extract data
        questions = data.get('questions', [])
        answers = data.get('answers', [])
        duration = data.get('duration', 0)
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Analyze the interview performance
        report_data = analyze_interview_performance(questions, answers, duration)
        
        # Create report record
        report = TechnicalInterviewReport.objects.create(
            session_id=session_id,
            user=request.user if request.user.is_authenticated else None,
            questions_data=questions,
            answers_data=answers,
            duration=duration,
            overall_score=report_data['overall_score'],
            performance_level=report_data['performance_level'],
            strengths=report_data['strengths'],
            improvements=report_data['improvements'],
            skill_scores=report_data['skill_scores'],
            question_reviews=report_data['question_reviews'],
            recommendations=report_data['recommendations'],
            questions_answered=report_data['questions_answered'],
            average_answer_length=report_data['average_answer_length'],
            voice_answers_count=report_data['voice_answers_count'],
            text_answers_count=report_data['text_answers_count']
        )
        
        return JsonResponse({
            'success': True,
            'report_id': session_id
        })
        
    except Exception as e:
        print(f"Report generation error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def interview_report(request, report_id):
    """Display the interview report"""
    try:
        report = TechnicalInterviewReport.objects.get(session_id=report_id)
        
        context = {
            'report': report,
        }
        
        return render(request, 'interview/interview_report.html', context)
        
    except TechnicalInterviewReport.DoesNotExist:
        return render(request, '404.html', status=404)
