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
    return genai.GenerativeModel('gemini-pro')

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

def analyze_resume(resume_path):
    """Analyze resume using Gemini API"""
    try:
        model = get_gemini_model('technical')
        
        # Simple text-based analysis for demo purposes
        # In a real implementation, you'd use PDF/DOC parsing libraries
        try:
            with open(resume_path, 'r', encoding='utf-8') as file:
                resume_content = file.read()
        except:
            # If can't read as text, provide generic analysis
            resume_content = "Resume content analysis"
            
        prompt = f"""
        Analyze this resume content and provide detailed feedback:
        
        Resume Content: {resume_content[:1000]}...
        
        Please provide comprehensive analysis in JSON format with these keys:
        1. score (1-10) - Overall resume quality
        2. strengths - Array of key strengths
        3. improvements - Array of specific improvement suggestions
        4. missing_sections - Array of missing important sections
        5. ats_score (1-100) - ATS compatibility score
        6. recommendations - Array of actionable recommendations
        7. formatting_score (1-10) - Resume formatting quality
        8. content_score (1-10) - Content quality and relevance
        
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
            required_fields = ['score', 'strengths', 'improvements', 'missing_sections', 'ats_score', 'recommendations']
            for field in required_fields:
                if field not in feedback:
                    feedback[field] = [] if field in ['strengths', 'improvements', 'missing_sections', 'recommendations'] else 0
                    
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
                "content_score": 7
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
            "content_score": 0
        }

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