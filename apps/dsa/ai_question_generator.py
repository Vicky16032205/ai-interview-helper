import google.generativeai as genai
import random
import json
import logging
import time
from django.conf import settings
from .models import DSAQuestion

# Setup logging
logger = logging.getLogger(__name__)

class AIQuestionGenerator:
    """Generate DSA questions dynamically using Google Gemini AI"""
    
    def __init__(self):
        # Configure Gemini API
        gemini_api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Gemini AI model initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini model: {e}")
                self.model = None
        else:
            logger.warning("⚠️ GEMINI_API_KEY not found in settings - using fallback questions only")
            self.model = None
        
        self.difficulty_levels = ['easy', 'medium', 'hard']
        self.categories = [
            'array', 'string', 'linkedlist', 'tree', 'graph', 
            'dp', 'sorting', 'searching', 'stack', 'queue', 
            'heap', 'backtracking', 'greedy', 'math', 'bit-manipulation'
        ]
        
        self.prompts = {
            'easy': {
                'array': "Generate an easy array problem similar to 'Two Sum' or 'Remove Duplicates'",
                'string': "Generate an easy string problem like 'Valid Palindrome' or 'First Unique Character'",
                'linkedlist': "Generate an easy linked list problem like 'Merge Two Sorted Lists'",
                'tree': "Generate an easy tree problem like 'Maximum Depth of Binary Tree'",
                'stack': "Generate an easy stack problem like 'Valid Parentheses'",
            },
            'medium': {
                'array': "Generate a medium array problem involving two pointers or sliding window",
                'string': "Generate a medium string problem with pattern matching or manipulation",
                'tree': "Generate a medium tree problem involving traversal or construction",
                'dp': "Generate a medium dynamic programming problem like '0/1 Knapsack variation'",
                'graph': "Generate a medium graph problem using BFS or DFS",
            },
            'hard': {
                'array': "Generate a hard array problem with complex optimization requirements",
                'dp': "Generate a hard dynamic programming problem with multiple states",
                'graph': "Generate a hard graph problem involving shortest path or network flow",
                'tree': "Generate a hard tree problem with advanced tree algorithms",
                'backtracking': "Generate a hard backtracking problem with pruning optimization",
            }
        }

    def generate_question(self, difficulty=None, category=None, user_preferences=None):
        """Generate a single DSA question dynamically"""
        
        if not difficulty:
            difficulty = random.choice(self.difficulty_levels)
        if not category:
            category = random.choice(self.categories)
            
        # Get appropriate prompt
        prompt_base = self.prompts.get(difficulty, {}).get(category, 
            f"Generate a {difficulty} level {category} programming problem")
        
        # Construct detailed prompt
        prompt = f"""
        You are an expert technical interviewer creating coding problems for software engineering interviews.
        
        {prompt_base}
        
        Create a coding interview question with the following structure:
        1. Title: A clear, concise problem title
        2. Description: Detailed problem statement (2-3 paragraphs)
        3. Examples: At least 2 input/output examples with explanations
        4. Constraints: Technical constraints and limits
        5. Time Complexity: Expected optimal time complexity
        6. Space Complexity: Expected optimal space complexity
        7. Hints: 2-3 solution hints without giving away the answer
        
        Requirements:
        - Make it realistic for a {difficulty} level {category} interview question
        - Ensure the problem is original but follows common interview patterns
        - Include clear test cases and edge cases
        - Provide practical constraints similar to LeetCode problems
        
        IMPORTANT: Return ONLY a valid JSON object with these exact keys:
        {{"title", "description", "examples", "constraints", "time_complexity", "space_complexity", "hints"}}
        
        Do not include any markdown formatting, explanations, or text outside the JSON.
        """
        
        try:
            if not self.model:
                logger.info("🔄 Using fallback question generation (Gemini not available)")
                return self._generate_fallback_question(difficulty, category)
            
            logger.info(f"🤖 Generating {difficulty} {category} question using Gemini AI")
            
            # Retry logic for API calls
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Generate content using Gemini with timeout
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,
                            top_p=0.8,
                            top_k=40,
                            max_output_tokens=2048,
                        ),
                        # Add safety settings to avoid blocks
                        safety_settings=[
                            {
                                "category": "HARM_CATEGORY_HARASSMENT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_HATE_SPEECH",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            }
                        ]
                    )
                    
                    # If we get here, the API call succeeded
                    break
                    
                except Exception as api_error:
                    logger.warning(f"🔄 Gemini API attempt {attempt + 1} failed: {api_error}")
                    if attempt < max_retries - 1:
                        # Wait before retrying (exponential backoff)
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        logger.info(f"⏳ Retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                    else:
                        # All retries failed, use fallback
                        logger.error(f"❌ All Gemini API retries failed, using fallback")
                        return self._generate_fallback_question(difficulty, category)
            
            # Extract and parse the response
            response_text = response.text.strip()
            logger.debug(f"Raw Gemini response: {response_text[:200]}...")
            
            # Clean up response text to ensure it's valid JSON
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            question_data = json.loads(response_text)
            
            # Add metadata
            question_data.update({
                'difficulty': difficulty,
                'category': category,
                'generated': True,
                'leetcode_url': ''  # Generated questions won't have LeetCode links
            })
            
            logger.info(f"✅ Successfully generated question: {question_data.get('title', 'Unknown')}")
            return question_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            # Fallback to template-based generation if JSON parsing fails
            return self._generate_fallback_question(difficulty, category)
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}")
            # Fallback to template-based generation if AI fails
            return self._generate_fallback_question(difficulty, category)

    def generate_question_set(self, count=5, difficulty_mix=None, categories=None):
        """Generate a set of questions for practice session"""
        
        if not difficulty_mix:
            difficulty_mix = {'easy': 2, 'medium': 2, 'hard': 1}
        
        if not categories:
            categories = random.sample(self.categories, min(count, len(self.categories)))
        
        questions = []
        
        # Generate based on difficulty mix
        for difficulty, num_questions in difficulty_mix.items():
            for _ in range(num_questions):
                category = random.choice(categories)
                question = self.generate_question(difficulty, category)
                questions.append(question)
        
        return questions

    def generate_adaptive_question(self, user_performance_history):
        """Generate question based on user's performance history"""
        
        # Analyze user performance
        if not user_performance_history:
            return self.generate_question('easy', 'array')
        
        # Calculate user skill level
        recent_performance = user_performance_history[-10:]  # Last 10 questions
        success_rate = sum(1 for q in recent_performance if q.get('solved', False)) / len(recent_performance)
        
        # Adapt difficulty based on performance
        if success_rate > 0.8:
            # User is doing well, increase difficulty
            difficulty = 'hard' if random.random() < 0.6 else 'medium'
        elif success_rate > 0.5:
            # User is average, maintain medium level
            difficulty = 'medium' if random.random() < 0.7 else 'easy'
        else:
            # User is struggling, provide easier questions
            difficulty = 'easy' if random.random() < 0.8 else 'medium'
        
        # Find weak categories
        category_performance = {}
        for q in recent_performance:
            cat = q.get('category', 'array')
            if cat not in category_performance:
                category_performance[cat] = []
            category_performance[cat].append(q.get('solved', False))
        
        # Focus on weak areas
        weak_categories = [cat for cat, results in category_performance.items() 
                          if sum(results) / len(results) < 0.5]
        
        category = random.choice(weak_categories) if weak_categories else random.choice(self.categories)
        
        return self.generate_question(difficulty, category)

    def _generate_fallback_question(self, difficulty, category):
        """Fallback question generation using templates"""
        
        templates = {
            'easy': {
                'array': {
                    'title': f'Find Target in Sorted Array - {random.randint(1, 100)}',
                    'description': 'Given a sorted array of integers and a target value, determine if the target exists in the array. Return true if found, false otherwise.',
                    'examples': 'Input: nums = [1,2,3,4,5], target = 3\nOutput: true\n\nInput: nums = [1,3,5,7,9], target = 6\nOutput: false',
                    'constraints': '1 <= nums.length <= 1000\n-1000 <= nums[i] <= 1000\nArray is sorted in ascending order',
                    'time_complexity': 'O(log n)',
                    'space_complexity': 'O(1)',
                    'hints': 'Since array is sorted, consider binary search. Handle edge cases with empty arrays.'
                },
                'string': {
                    'title': f'Valid Palindrome Check - {random.randint(1, 100)}',
                    'description': 'Given a string, determine if it is a valid palindrome, considering only alphanumeric characters and ignoring cases.',
                    'examples': 'Input: s = "A man a plan a canal Panama"\nOutput: true\n\nInput: s = "race a car"\nOutput: false',
                    'constraints': '1 <= s.length <= 2 * 10^5\ns consists only of printable ASCII characters',
                    'time_complexity': 'O(n)',
                    'space_complexity': 'O(1)',
                    'hints': 'Use two pointers approach. Convert to lowercase and skip non-alphanumeric characters.'
                },
                'linkedlist': {
                    'title': f'Remove Duplicates from Sorted List - {random.randint(1, 100)}',
                    'description': 'Given the head of a sorted linked list, delete all duplicates such that each element appears only once.',
                    'examples': 'Input: head = [1,1,2]\nOutput: [1,2]\n\nInput: head = [1,1,2,3,3]\nOutput: [1,2,3]',
                    'constraints': 'The number of nodes in the list is in the range [0, 300]\n-100 <= Node.val <= 100\nThe list is guaranteed to be sorted in ascending order',
                    'time_complexity': 'O(n)',
                    'space_complexity': 'O(1)',
                    'hints': 'Traverse the list and compare current node with next. Skip duplicates.'
                }
            },
            'medium': {
                'array': {
                    'title': f'Subarray Sum Equals K - {random.randint(1, 100)}',
                    'description': 'Given an array of integers nums and an integer k, return the total number of continuous subarrays whose sum equals to k.',
                    'examples': 'Input: nums = [1,1,1], k = 2\nOutput: 2\n\nInput: nums = [1,2,3], k = 3\nOutput: 2',
                    'constraints': '1 <= nums.length <= 2 * 10^4\n-1000 <= nums[i] <= 1000\n-10^7 <= k <= 10^7',
                    'time_complexity': 'O(n)',
                    'space_complexity': 'O(n)',
                    'hints': 'Use prefix sum and hash map. For each position, check if (current_sum - k) exists in map.'
                },
                'tree': {
                    'title': f'Binary Tree Level Order Traversal - {random.randint(1, 100)}',
                    'description': 'Given the root of a binary tree, return the level order traversal of its nodes values (i.e., from left to right, level by level).',
                    'examples': 'Input: root = [3,9,20,null,null,15,7]\nOutput: [[3],[9,20],[15,7]]',
                    'constraints': 'The number of nodes in the tree is in the range [0, 2000]\n-1000 <= Node.val <= 1000',
                    'time_complexity': 'O(n)',
                    'space_complexity': 'O(n)',
                    'hints': 'Use BFS with queue. Process nodes level by level using queue size.'
                },
                'dp': {
                    'title': f'Coin Change Problem - {random.randint(1, 100)}',
                    'description': 'You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money. Return the fewest number of coins needed to make up that amount.',
                    'examples': 'Input: coins = [1,3,4], amount = 6\nOutput: 2\nExplanation: 6 = 3 + 3\n\nInput: coins = [2], amount = 3\nOutput: -1',
                    'constraints': '1 <= coins.length <= 12\n1 <= coins[i] <= 2^31 - 1\n0 <= amount <= 10^4',
                    'time_complexity': 'O(amount * coins.length)',
                    'space_complexity': 'O(amount)',
                    'hints': 'Use dynamic programming. For each amount, try all coin denominations.'
                }
            },
            'hard': {
                'array': {
                    'title': f'Trapping Rain Water - {random.randint(1, 100)}',
                    'description': 'Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.',
                    'examples': 'Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]\nOutput: 6\nExplanation: The above elevation map can trap 6 units of rain water.',
                    'constraints': 'n == height.length\n1 <= n <= 2 * 10^4\n0 <= height[i] <= 3 * 10^4',
                    'time_complexity': 'O(n)',
                    'space_complexity': 'O(1)',
                    'hints': 'Use two pointers from both ends. Track maximum heights from left and right.'
                },
                'graph': {
                    'title': f'Word Ladder Transformation - {random.randint(1, 100)}',
                    'description': 'Given two words beginWord and endWord, and a dictionary wordList, find the length of shortest transformation sequence from beginWord to endWord, changing only one letter at a time.',
                    'examples': 'Input: beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]\nOutput: 5\nExplanation: "hit" -> "hot" -> "dot" -> "dog" -> "cog"',
                    'constraints': '1 <= beginWord.length <= 10\nendWord.length == beginWord.length\n1 <= wordList.length <= 5000\nwordList[i].length == beginWord.length',
                    'time_complexity': 'O(M^2 * N)',
                    'space_complexity': 'O(M^2 * N)',
                    'hints': 'Use BFS to find shortest path. Build graph of word transformations first.'
                },
                'dp': {
                    'title': f'Edit Distance - {random.randint(1, 100)}',
                    'description': 'Given two strings word1 and word2, return the minimum number of operations required to convert word1 to word2. You can insert, delete or replace any character.',
                    'examples': 'Input: word1 = "horse", word2 = "ros"\nOutput: 3\nExplanation: horse -> rorse (replace h with r) -> rose (remove r) -> ros (remove e)',
                    'constraints': '0 <= word1.length, word2.length <= 500\nword1 and word2 consist of lowercase English letters',
                    'time_complexity': 'O(m * n)',
                    'space_complexity': 'O(m * n)',
                    'hints': 'Use 2D DP table. Consider three operations: insert, delete, replace.'
                }
            }
        }
        
        # Get template based on difficulty and category
        difficulty_templates = templates.get(difficulty, templates['medium'])
        template = difficulty_templates.get(category, difficulty_templates.get('array', templates['easy']['array']))
        
        # Create a copy to avoid modifying the original template
        result = template.copy()
        result.update({
            'difficulty': difficulty,
            'category': category,
            'generated': True,
            'fallback': True,  # Mark as fallback generation
            'leetcode_url': ''
        })
        
        return result

    def save_generated_question(self, question_data):
        """Save generated question to database for caching"""
        
        # Create new DSAQuestion instance
        question = DSAQuestion.objects.create(
            title=question_data['title'],
            description=question_data['description'],
            difficulty=question_data['difficulty'],
            category=question_data['category'],
            examples=question_data['examples'],
            constraints=question_data['constraints'],
            time_complexity=question_data['time_complexity'],
            space_complexity=question_data['space_complexity'],
            leetcode_url=question_data.get('leetcode_url', '')
        )
        
        return question

    def generate_question_batch(self, count=5, difficulty='medium', categories=None, recent_concepts=None):
        """Generate multiple questions in a single batch request for efficiency"""
        
        if not categories:
            categories = random.sample(self.categories, min(count, len(self.categories)))
        
        if recent_concepts is None:
            recent_concepts = []
        
        # Create comprehensive batch prompt
        batch_prompt = f"""
        You are an expert technical interviewer creating multiple coding problems for software engineering interviews.
        
        Generate EXACTLY {count} DIFFERENT and UNIQUE {difficulty} level DSA problems covering these categories: {', '.join(categories[:count])}.
        
        Requirements for EACH question:
        1. Must be completely UNIQUE and DIFFERENT from each other
        2. Different algorithmic approaches and patterns
        3. Avoid these recently used concepts: {', '.join(recent_concepts)}
        4. Cover diverse problem-solving techniques
        
        For each question, provide:
        - title: Clear, concise problem title
        - description: Detailed problem statement (2-3 paragraphs)
        - examples: At least 2 input/output examples with explanations
        - constraints: Technical constraints and limits
        - time_complexity: Expected optimal time complexity
        - space_complexity: Expected optimal space complexity
        - hints: 2-3 solution hints without giving away the answer
        - category: One of {categories[:count]}
        - difficulty: "{difficulty}"
        
        CRITICAL: Return ONLY a valid JSON array containing {count} question objects.
        Each object must have ALL these keys: title, description, examples, constraints, time_complexity, space_complexity, hints, category, difficulty.
        
        Ensure each question is:
        - Realistic for {difficulty} level interviews
        - Original but follows common patterns
        - Has clear test cases and edge cases
        - Different algorithmic approach from others in the batch
        
        Example format:
        [
          {{"title": "Problem 1", "description": "...", "examples": "...", "constraints": "...", "time_complexity": "...", "space_complexity": "...", "hints": "...", "category": "{categories[0] if categories else 'array'}", "difficulty": "{difficulty}"}},
          {{"title": "Problem 2", "description": "...", "examples": "...", "constraints": "...", "time_complexity": "...", "space_complexity": "...", "hints": "...", "category": "{categories[1] if len(categories) > 1 else 'string'}", "difficulty": "{difficulty}"}}
        ]
        
        Return ONLY the JSON array, no explanations or markdown.
        """
        
        try:
            if not self.model:
                logger.info("🔄 Batch generation using fallback method (Gemini not available)")
                return [self._generate_fallback_question(difficulty, categories[i % len(categories)]) 
                       for i in range(count)]
            
            logger.info(f"🤖 Generating batch of {count} {difficulty} questions using Gemini AI")
            
            # Retry logic for API calls
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(
                        batch_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.8,  # Slightly higher for more variety
                            top_p=0.9,
                            top_k=50,
                            max_output_tokens=4096,  # Larger limit for batch
                        ),
                        safety_settings=[
                            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
                        ]
                    )
                    break
                    
                except Exception as api_error:
                    logger.warning(f"🔄 Batch generation attempt {attempt + 1} failed: {api_error}")
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        logger.info(f"⏳ Retrying batch generation in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"❌ All batch generation retries failed, using fallback")
                        return [self._generate_fallback_question(difficulty, categories[i % len(categories)]) 
                               for i in range(count)]
            
            # Process response
            response_text = response.text.strip()
            logger.debug(f"Raw batch response: {response_text[:300]}...")
            
            # Clean up response
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse JSON array
            questions_data = json.loads(response_text)
            
            if not isinstance(questions_data, list):
                raise ValueError("Response is not a JSON array")
            
            # Add metadata to each question
            for i, question_data in enumerate(questions_data):
                question_data.update({
                    'generated': True,
                    'leetcode_url': '',
                    'id': f"batch_{i}_{hash(question_data.get('title', f'question_{i}'))}"
                })
            
            logger.info(f"✅ Successfully generated batch of {len(questions_data)} questions")
            return questions_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Batch JSON parsing error: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            # Fallback to individual generation
            return [self._generate_fallback_question(difficulty, categories[i % len(categories)]) 
                   for i in range(count)]
        except Exception as e:
            logger.error(f"❌ Batch generation error: {e}")
            # Fallback to individual generation
            return [self._generate_fallback_question(difficulty, categories[i % len(categories)]) 
                   for i in range(count)]

# Usage examples:
"""
# Generate single question
generator = AIQuestionGenerator()
question = generator.generate_question(difficulty='medium', category='array')

# Generate practice set
questions = generator.generate_question_set(count=5)

# Generate adaptive question
user_history = [{'solved': True, 'category': 'array'}, {'solved': False, 'category': 'tree'}]
adaptive_question = generator.generate_adaptive_question(user_history)
"""
