from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import DSAQuestion

def dsa_questions(request):
    """Display DSA practice questions"""
    difficulty = request.GET.get('difficulty', 'all')
    category = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '')
    
    questions = DSAQuestion.objects.all()
    
    # Apply filters
    if difficulty != 'all':
        questions = questions.filter(difficulty=difficulty)
    
    if category != 'all':
        questions = questions.filter(category=category)
    
    if search_query:
        questions = questions.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Get counts for stats
    all_questions = DSAQuestion.objects.all()
    easy_count = all_questions.filter(difficulty='easy').count()
    medium_count = all_questions.filter(difficulty='medium').count()
    hard_count = all_questions.filter(difficulty='hard').count()
    
    # Pagination
    paginator = Paginator(questions, 12)  # Show 12 questions per page
    page_number = request.GET.get('page')
    questions = paginator.get_page(page_number)
    
    context = {
        'questions': questions,
        'difficulties': ['easy', 'medium', 'hard'],
        'categories': DSAQuestion.CATEGORY_CHOICES,
        'selected_difficulty': difficulty,
        'selected_category': category,
        'search_query': search_query,
        'easy_count': easy_count,
        'medium_count': medium_count,
        'hard_count': hard_count,
    }
    
    return render(request, 'dsa/questions.html', context)

def dsa_practice(request):
    """DSA practice session page"""
    # Get a random question or allow user to select
    questions = DSAQuestion.objects.all().order_by('?')[:5]  # Random 5 questions
    context = {
        'questions': questions,
    }
    return render(request, 'dsa/practice.html', context)

def dsa_solve(request, question_id):
    """Individual question solving page"""
    question = get_object_or_404(DSAQuestion, id=question_id)
    context = {
        'question': question,
    }
    return render(request, 'dsa/solve.html', context)

def get_question_detail(request, question_id):
    """Get detailed information about a specific question"""
    try:
        question = DSAQuestion.objects.get(id=question_id)
        return JsonResponse({
            'success': True,
            'question': {
                'id': question.id,
                'title': question.title,
                'description': question.description,
                'difficulty': question.difficulty,
                'category': question.category,
                'examples': question.examples,
                'constraints': question.constraints,
                'solution_approach': question.solution_approach,
                'time_complexity': question.time_complexity,
                'space_complexity': question.space_complexity,
            }
        })
    except DSAQuestion.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Question not found'
        }, status=404)