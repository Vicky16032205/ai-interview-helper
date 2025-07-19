from django.core.management.base import BaseCommand
from apps.dsa.ai_question_generator import AIQuestionGenerator

class Command(BaseCommand):
    help = 'Test the AI question generator functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--difficulty',
            type=str,
            default='easy',
            help='Question difficulty (easy, medium, hard)'
        )
        parser.add_argument(
            '--category',
            type=str,
            default='array',
            help='Question category (array, string, tree, etc.)'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of questions to generate'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🤖 Testing Gemini AI Question Generator')
        )
        
        try:
            generator = AIQuestionGenerator()
            
            # Check Gemini configuration
            if generator.model:
                self.stdout.write(
                    self.style.SUCCESS('✅ Gemini AI model configured and ready')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ Gemini not available - using fallback templates')
                )
            
            # Generate questions
            difficulty = options['difficulty']
            category = options['category']
            count = options['count']
            
            self.stdout.write(f"\nGenerating {count} {difficulty} {category} question(s)...")
            
            for i in range(count):
                try:
                    question = generator.generate_question(
                        difficulty=difficulty, 
                        category=category
                    )
                    
                    self.stdout.write(f"\n--- Question {i+1} ---")
                    self.stdout.write(f"Title: {question['title']}")
                    self.stdout.write(f"Difficulty: {question['difficulty']}")
                    self.stdout.write(f"Category: {question['category']}")
                    self.stdout.write(f"Generated: {question.get('generated', False)}")
                    self.stdout.write(f"Fallback: {question.get('fallback', False)}")
                    self.stdout.write(f"Time Complexity: {question.get('time_complexity', 'N/A')}")
                    self.stdout.write(f"Space Complexity: {question.get('space_complexity', 'N/A')}")
                    self.stdout.write(f"Description: {question['description'][:150]}...")
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Error generating question {i+1}: {e}")
                    )
            
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Test completed!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'💥 Test failed: {e}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())
