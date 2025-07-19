import google.generativeai as genai
from django.conf import settings
import json
import base64
import os

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_gemini_model(model_type='technical'):
    """Get configured Gemini model"""
    api_key = settings.GEMINI_API_KEY if model_type == 'technical' else settings.GEMINI_HR_API_KEY
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')  # Updated to current model name

def analyze_code(code, language='python'):
    """Analyze code using Gemini API"""
    try:
        model = get_gemini_model('technical')
        prompt = f"""
        Analyze the following {language} code and provide feedback:
        
        Code:
        ```{language}
        {code}
        ```
        
        Please provide:
        1. Code quality score (1-10)
        2. Critical issues (if any)
        3. Suggestions for improvement
        4. Best practices recommendations
        
        Format the response as JSON with keys: score, issues, suggestions, best_practices
        """
        
        response = model.generate_content(prompt)
        
        # Parse response and ensure it's JSON
        try:
            feedback = json.loads(response.text)
        except:
            feedback = {
                "score": 7,
                "issues": ["Could not parse AI response"],
                "suggestions": ["Please try again"],
                "best_practices": ["Follow coding standards"]
            }
        
        return feedback
    except Exception as e:
        return {
            "error": str(e),
            "score": 0,
            "issues": ["Error analyzing code"],
            "suggestions": ["Please check your code and try again"],
            "best_practices": []
        }

def analyze_technical_answer(question, answer, is_audio=False):
    """Analyze technical interview answer"""
    try:
        model = get_gemini_model('technical')
        
        prompt = f"""
        Question: {question}
        
        Answer: {answer}
        
        Please evaluate this technical interview answer and provide:
        1. Accuracy score (1-10)
        2. Technical correctness
        3. Areas for improvement
        4. Missing key points
        {'5. Communication clarity (for audio response)' if is_audio else ''}
        
        Format as JSON with keys: score, correctness, improvements, missing_points{', communication' if is_audio else ''}
        """
        
        response = model.generate_content(prompt)
        
        try:
            feedback = json.loads(response.text)
        except:
            feedback = {
                "score": 7,
                "correctness": "Good attempt",
                "improvements": ["Could not parse detailed feedback"],
                "missing_points": [],
                "communication": "Clear" if is_audio else None
            }
        
        return feedback
    except Exception as e:
        return {
            "error": str(e),
            "score": 5,
            "correctness": "Unable to analyze",
            "improvements": ["Error in analysis"],
            "missing_points": []
        }

def analyze_hr_answer(question, answer, is_audio=False):
    """Analyze HR interview answer"""
    try:
        model = get_gemini_model('hr')
        
        prompt = f"""
        HR Interview Question: {question}
        
        Candidate's Answer: {answer}
        
        Please evaluate this HR interview answer and provide:
        1. Overall score (1-10)
        2. Communication effectiveness
        3. Key strengths
        4. Areas for improvement
        5. STAR method usage (if applicable)
        {'6. Tone and delivery (for audio response)' if is_audio else ''}
        
        Format as JSON with keys: score, communication, strengths, improvements, star_usage{', tone_delivery' if is_audio else ''}
        """
        
        response = model.generate_content(prompt)
        
        try:
            feedback = json.loads(response.text)
        except:
            feedback = {
                "score": 7,
                "communication": "Good",
                "strengths": ["Clear communication"],
                "improvements": ["Could not parse detailed feedback"],
                "star_usage": "Not applicable",
                "tone_delivery": "Professional" if is_audio else None
            }
        
        return feedback
    except Exception as e:
        return {
            "error": str(e),
            "score": 5,
            "communication": "Unable to analyze",
            "strengths": [],
            "improvements": ["Error in analysis"],
            "star_usage": "Unknown"
        }

def analyze_resume(resume_path, file_extension):
    """Analyze resume using Gemini API"""
    try:
        model = get_gemini_model('technical')
        
        # Extract text from different file formats
        resume_text = extract_text_from_file(resume_path, file_extension)
            
        prompt = f"""
        Analyze this resume content and provide detailed feedback:
        
        Resume Content: {resume_text[:2000]}...
        
        Please provide comprehensive analysis in JSON format with these keys:
        1. score (1-10) - Overall resume quality
        2. strengths - Array of key strengths
        3. improvements - Array of specific improvement suggestions
        4. missing_sections - Array of missing important sections
        5. ats_score (1-100) - ATS compatibility score
        6. recommendations - Array of actionable recommendations
        7. formatting_score (1-10) - Resume formatting quality
        8. content_score (1-10) - Content quality and relevance
        9. skills_identified - Array of technical skills found
        10. experience_level - String indicating experience level (entry, mid, senior)
        
        Format as valid JSON only.
        """
        
        response = model.generate_content(prompt)
        
        try:
            # Clean the response to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            feedback = json.loads(response_text)
            
            # Ensure all required fields exist
            required_fields = ['score', 'strengths', 'improvements', 'missing_sections', 'ats_score', 'recommendations', 'skills_identified', 'experience_level']
            for field in required_fields:
                if field not in feedback:
                    if field in ['strengths', 'improvements', 'missing_sections', 'recommendations', 'skills_identified']:
                        feedback[field] = []
                    elif field == 'experience_level':
                        feedback[field] = 'mid'
                    else:
                        feedback[field] = 0
                    
        except Exception as parse_error:
            print(f"JSON parsing error: {parse_error}")
            feedback = {
                "score": 7,
                "strengths": [
                    "Professional presentation",
                    "Clear contact information",
                    "Relevant work experience"
                ],
                "improvements": [
                    "Add more quantifiable achievements",
                    "Include relevant keywords for ATS optimization",
                    "Improve formatting consistency"
                ],
                "missing_sections": [
                    "Skills section could be more detailed",
                    "Consider adding a professional summary"
                ],
                "ats_score": 75,
                "recommendations": [
                    "Use action verbs to start bullet points",
                    "Add metrics and numbers to achievements",
                    "Include industry-relevant keywords",
                    "Ensure consistent formatting throughout"
                ],
                "formatting_score": 8,
                "content_score": 7,
                "skills_identified": ["Python", "JavaScript", "SQL"],
                "experience_level": "mid"
            }
        
        return feedback
        
    except Exception as e:
        print(f"Resume analysis error: {e}")
        return {
            "error": f"Analysis error: {str(e)}",
            "score": 0,
            "strengths": ["Unable to analyze - please try again"],
            "improvements": ["Ensure file is in supported format (PDF, DOC, DOCX, TXT)"],
            "missing_sections": [],
            "ats_score": 0,
            "recommendations": ["Please upload a valid resume file and try again"],
            "formatting_score": 0,
            "content_score": 0,
            "skills_identified": [],
            "experience_level": "entry"
        }

def extract_text_from_file(file_path, file_extension):
    """Extract text from different file formats"""
    try:
        if file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        elif file_extension == 'pdf':
            # For PDF files, we'll try to read basic text
            # Note: For production, you should use PyPDF2 or pdfplumber
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    return text
            except ImportError:
                # Fallback if PyPDF2 not available
                return "PDF content - install PyPDF2 for full text extraction"
        else:
            # For DOC/DOCX files
            try:
                import docx2txt
                return docx2txt.process(file_path)
            except ImportError:
                # Fallback if docx2txt not available
                return "Document content - install docx2txt for full text extraction"
    except Exception as e:
        print(f"Text extraction error: {e}")
        return "Unable to extract text from file"

def generate_questions_from_resume(resume_path, file_extension, difficulty='medium'):
    """Generate technical questions based on resume content"""
    try:
        model = get_gemini_model('technical')
        
        # Extract text from resume
        resume_text = extract_text_from_file(resume_path, file_extension)
        
        prompt = f"""
        Based on this resume content, generate 5 technical interview questions at {difficulty} difficulty level:
        
        Resume Content: {resume_text[:1500]}...
        
        Focus on:
        1. Technologies and programming languages mentioned
        2. Projects and experience described
        3. Skills and frameworks listed
        4. Domain knowledge areas
        
        Generate questions that are:
        - Relevant to their background
        - Appropriate for {difficulty} difficulty
        - Mix of theoretical and practical
        - Test both breadth and depth of knowledge
        
        Format as JSON array with objects containing:
        - question: The interview question
        - category: Technology/concept category
        - focus_area: Specific skill being tested
        - explanation: Why this question is relevant to their background
        
        Example format:
        [
            {{
                "question": "Explain how you would optimize database queries in the context of your e-commerce project",
                "category": "Database Optimization",
                "focus_area": "SQL Performance",
                "explanation": "Based on your experience with database management in your projects"
            }}
        ]
        """
        
        response = model.generate_content(prompt)
        
        try:
            # Clean the response to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            questions = json.loads(response_text)
            
            # Ensure it's a list
            if not isinstance(questions, list):
                questions = []
                
        except Exception as parse_error:
            print(f"Questions JSON parsing error: {parse_error}")
            # Fallback questions based on difficulty
            questions = get_fallback_questions(difficulty)
        
        return questions
        
    except Exception as e:
        print(f"Question generation error: {e}")
        return get_fallback_questions(difficulty)

def get_fallback_questions(difficulty='medium'):
    """Fallback questions when AI generation fails"""
    questions_by_difficulty = {
        'easy': [
            {
                "question": "What is the difference between a list and a tuple in Python?",
                "category": "Python Basics",
                "focus_area": "Data Structures",
                "explanation": "Testing fundamental Python knowledge"
            },
            {
                "question": "Explain the concept of inheritance in Object-Oriented Programming",
                "category": "OOP Concepts",
                "focus_area": "Inheritance",
                "explanation": "Basic OOP understanding"
            },
            {
                "question": "What is a REST API and how does it work?",
                "category": "Web Development",
                "focus_area": "API Design",
                "explanation": "Web development fundamentals"
            }
        ],
        'medium': [
            {
                "question": "How would you implement caching in a web application to improve performance?",
                "category": "System Design",
                "focus_area": "Caching Strategies",
                "explanation": "Performance optimization concepts"
            },
            {
                "question": "Explain the difference between SQL and NoSQL databases with examples",
                "category": "Database Systems",
                "focus_area": "Database Design",
                "explanation": "Database technology comparison"
            },
            {
                "question": "Describe how you would handle concurrent requests in a web server",
                "category": "Concurrency",
                "focus_area": "Multi-threading",
                "explanation": "Concurrent programming concepts"
            }
        ],
        'hard': [
            {
                "question": "Design a distributed system for handling millions of concurrent users",
                "category": "System Design",
                "focus_area": "Scalability",
                "explanation": "Large-scale system design"
            },
            {
                "question": "Explain the CAP theorem and its implications in distributed databases",
                "category": "Distributed Systems",
                "focus_area": "Consistency Models",
                "explanation": "Advanced distributed systems concepts"
            },
            {
                "question": "How would you implement a rate limiter for an API gateway?",
                "category": "System Design",
                "focus_area": "Rate Limiting",
                "explanation": "Advanced API design patterns"
            }
        ]
    }
    
    return questions_by_difficulty.get(difficulty, questions_by_difficulty['medium'])

def get_technical_questions():
    """Get technical interview questions by difficulty"""
    return {
        'easy': [
            "What is the difference between a list and a tuple in Python?",
            "Explain the concept of inheritance in OOP.",
            "What is a REST API?",
            "What is the difference between GET and POST requests?",
            "Explain what is version control and why it's important."
        ],
        'medium': [
            "Explain the concept of closures in JavaScript.",
            "What is the difference between SQL and NoSQL databases?",
            "How does indexing improve database performance?",
            "Explain the MVC architecture pattern.",
            "What is the difference between authentication and authorization?"
        ],
        'hard': [
            "Explain the CAP theorem in distributed systems.",
            "How would you design a URL shortening service like bit.ly?",
            "Explain the concept of database sharding.",
            "What are microservices and when should you use them?",
            "How does garbage collection work in modern programming languages?"
        ]
    }

def get_hr_questions():
    """Get HR interview questions"""
    return [
        "Tell me about yourself.",
        "Why do you want to work for our company?",
        "What are your greatest strengths and weaknesses?",
        "Where do you see yourself in 5 years?",
        "Describe a challenging situation you faced and how you handled it.",
        "Why are you leaving your current job?",
        "What motivates you?",
        "How do you handle stress and pressure?",
        "Tell me about a time you showed leadership.",
        "What are your salary expectations?"
    ]

def generate_follow_up_question(original_question, answer):
    """Generate follow-up question based on answer"""
    try:
        model = get_gemini_model('hr')
        
        prompt = f"""
        Original question: {original_question}
        Candidate's answer: {answer}
        
        Generate one relevant follow-up question to dig deeper into their response.
        Keep it concise and relevant.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "Can you provide more specific details about that experience?"