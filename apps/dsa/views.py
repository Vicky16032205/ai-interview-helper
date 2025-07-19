from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import DSAQuestion
from .ai_question_generator import AIQuestionGenerator

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
    """DSA practice session page with dynamic question generation"""
    # Get user preferences
    generate_new = request.GET.get('generate_new', 'false').lower() == 'true'
    difficulty_preference = request.GET.get('difficulty', 'mixed')
    category_preference = request.GET.get('category', 'mixed')
    
    if generate_new:
        # Generate new questions dynamically
        generator = AIQuestionGenerator()
        
        if difficulty_preference == 'mixed':
            # Mixed difficulty set
            generated_questions = generator.generate_question_set(
                count=5,
                difficulty_mix={'easy': 2, 'medium': 2, 'hard': 1}
            )
        else:
            # Specific difficulty
            generated_questions = []
            for _ in range(5):
                category = None if category_preference == 'mixed' else category_preference
                question_data = generator.generate_question(
                    difficulty=difficulty_preference, 
                    category=category
                )
                generated_questions.append(question_data)
        
        # Convert to question-like objects for template
        questions = []
        for q_data in generated_questions:
            # Create temporary question object
            question = type('Question', (), q_data)()
            question.id = f"generated_{len(questions)}"
            question.get_difficulty_display = lambda: q_data['difficulty'].title()
            question.get_category_display = lambda: q_data['category'].replace('_', ' ').title()
            questions.append(question)
    else:
        # Use existing questions from database (fallback)
        questions = DSAQuestion.objects.all().order_by('?')[:5]
    
    context = {
        'questions': questions,
        'is_generated': generate_new,
        'difficulty_preference': difficulty_preference,
        'category_preference': category_preference,
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

@csrf_exempt
@csrf_exempt
def generate_dynamic_question(request):
    """Generate a new question dynamically using AI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            difficulty = data.get('difficulty', 'medium')
            category = data.get('category', 'array')
            save_to_db = data.get('save_to_db', False)
            
            generator = AIQuestionGenerator()
            question_data = generator.generate_question(difficulty, category)
            
            if save_to_db:
                # Save to database for future use
                saved_question = generator.save_generated_question(question_data)
                question_data['id'] = saved_question.id
                question_data['saved'] = True
            else:
                question_data['id'] = f"temp_{hash(question_data['title'])}"
                question_data['saved'] = False
            
            return JsonResponse({
                'success': True,
                'question': question_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

@csrf_exempt 
def generate_adaptive_question(request):
    """Generate question based on user performance"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_history = data.get('performance_history', [])
            
            generator = AIQuestionGenerator()
            question_data = generator.generate_adaptive_question(user_history)
            question_data['id'] = f"adaptive_{hash(question_data['title'])}"
            
            return JsonResponse({
                'success': True,
                'question': question_data,
                'adapted': True
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

@csrf_exempt
def generate_batch_questions(request):
    """Generate multiple questions in a single batch request"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            difficulty = data.get('difficulty', 'medium')
            categories = data.get('categories', ['array', 'string', 'linked_list', 'tree', 'graph'])
            count = data.get('count', 5)
            recent_concepts = data.get('recent_concepts', [])
            
            generator = AIQuestionGenerator()
            
            # Check if generator has batch generation method
            if hasattr(generator, 'generate_question_batch'):
                # Use dedicated batch generation if available
                questions = generator.generate_question_batch(
                    count=count,
                    difficulty=difficulty,
                    categories=categories,
                    recent_concepts=recent_concepts
                )
            else:
                # Fallback: Generate questions individually
                questions = []
                for i, category in enumerate(categories[:count]):
                    try:
                        question_data = generator.generate_question(difficulty, category)
                        question_data['id'] = f"batch_{i}_{hash(question_data['title'])}"
                        questions.append(question_data)
                    except Exception as e:
                        print(f"Error generating question for {category}: {e}")
                        continue
            
            return JsonResponse({
                'success': True,
                'questions': questions,
                'batch_size': len(questions),
                'method': 'batch' if hasattr(generator, 'generate_question_batch') else 'individual'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)