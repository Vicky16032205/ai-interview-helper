import google.generativeai as genai
from django.conf import settings
import json
import base64
import os
import PyPDF2
import docx
import re
import assemblyai as aai

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def clean_json_response(response_text):
    """Clean and extract JSON from Gemini API response"""
    try:
        # Remove markdown code blocks if present
        if "```json" in response_text:
            # Extract content between ```json and ```
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        elif "```" in response_text:
            # Extract content between ``` and ```
            json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        
        # Clean up the text
        response_text = response_text.strip()
        
        # Try to parse as JSON
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return a default structure
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text}")
        return None

def get_gemini_model(model_type='technical'):
    """Get configured Gemini model"""
    api_key = settings.GEMINI_API_KEY if model_type == 'technical' else settings.GEMINI_HR_API_KEY
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')  # Updated to current model name

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
        
        Please evaluate this HR interview answer and provide detailed feedback in JSON format:
        
        1. Overall score (1-10) - Rate the overall quality of the response
        2. Communication effectiveness - How well the candidate communicated their ideas
        3. Key strengths - List specific positive aspects of the answer (as array)
        4. Areas for improvement - List specific suggestions for enhancement (as array)
        5. STAR method usage - Whether the candidate used Situation-Task-Action-Result structure
        {'6. Tone and delivery - Assessment of voice quality and presentation' if is_audio else ''}
        
        Respond with ONLY a valid JSON object with these exact keys:
        {{
            "score": <number 1-10>,
            "communication": "<assessment of communication skills>",
            "strengths": ["<strength 1>", "<strength 2>", ...],
            "improvements": ["<improvement 1>", "<improvement 2>", ...],
            "star_usage": "<assessment of STAR method usage>"{f',\n            "tone_delivery": "<assessment of tone and delivery>"' if is_audio else ''}
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Debug: Print the raw response
        print(f"Raw Gemini response: {response.text}")
        
        # Use the clean_json_response function to properly parse the response
        feedback = clean_json_response(response.text)
        
        # Debug: Print the parsed feedback
        print(f"Parsed feedback: {feedback}")
        
        if feedback is None:
            print("JSON parsing failed, using fallback response")
            # If JSON parsing fails, provide a structured fallback
            feedback = {
                "score": 7,
                "communication": "Clear and understandable response provided",
                "strengths": [
                    "Addressed the question directly",
                    "Provided relevant information"
                ],
                "improvements": [
                    "Could provide more specific examples",
                    "Consider using the STAR method for better structure"
                ],
                "star_usage": "Partially applied - could be more structured"
            }
            if is_audio:
                feedback["tone_delivery"] = "Professional and clear"
        
        # Ensure all required fields exist with proper defaults
        required_fields = {
            'score': 7,
            'communication': 'Good communication',
            'strengths': ['Provided a relevant response'],
            'improvements': ['Consider providing more specific examples'],
            'star_usage': 'Not fully applied'
        }
        
        if is_audio:
            required_fields['tone_delivery'] = 'Professional'
        
        for field, default_value in required_fields.items():
            if field not in feedback or feedback[field] is None:
                feedback[field] = default_value
        
        return feedback
        
    except Exception as e:
        print(f"HR answer analysis error: {e}")
        error_response = {
            "score": 5,
            "communication": "Unable to analyze due to technical error",
            "strengths": ["Response was provided"],
            "improvements": ["Please try submitting your answer again"],
            "star_usage": "Could not be evaluated"
        }
        if is_audio:
            error_response["tone_delivery"] = "Could not be evaluated"
        return error_response

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

def transcribe_audio_with_assemblyai(audio_file_path):
    """Transcribe audio file using AssemblyAI API"""
    try:
        # Set up AssemblyAI API key
        aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
        
        # Configure transcription settings for better accuracy
        config = aai.TranscriptionConfig(
            language_code="en_us",
            punctuate=True,
            format_text=True,
            dual_channel=False,
            speaker_labels=False,
            # Enhanced features for interview context
            auto_highlights=True,
            sentiment_analysis=True,
            auto_chapters=False,
            entity_detection=True,
            iab_categories=False,
            content_safety=False,
            # Audio enhancement
            audio_start_from=0,
            audio_end_at=None,
            word_boost=[
                # Common interview terms for better recognition
                "experience", "skills", "project", "team", "leadership", 
                "challenge", "solution", "achievement", "responsibility",
                "communication", "collaboration", "problem-solving"
            ],
            boost_param="high"
        )
        
        print(f"Starting AssemblyAI transcription for: {audio_file_path}")
        
        # Create transcriber and transcribe
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_file_path)
        
        # Check if transcription was successful
        if transcript.status == aai.TranscriptStatus.error:
            print(f"AssemblyAI transcription failed: {transcript.error}")
            return f"Transcription failed: {transcript.error}"
        
        # Extract the text
        transcribed_text = transcript.text
        
        if not transcribed_text or transcribed_text.strip() == "":
            return "No speech detected in the audio. Please ensure you spoke clearly and try again."
        
        # Filter out very short transcriptions that might be noise
        if len(transcribed_text.strip().split()) < 3:
            return "Audio too short or unclear. Please provide a longer response and speak clearly."
        
        print(f"AssemblyAI transcription successful: {transcribed_text[:100]}...")
        
        # Return the transcribed text
        return transcribed_text.strip()
        
    except Exception as e:
        print(f"AssemblyAI transcription error: {e}")
        return f"Audio transcription failed: {str(e)}"

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using AssemblyAI API
    """
    print(f"Starting audio transcription with AssemblyAI for: {audio_file_path}")
    
    # Use AssemblyAI for transcription
    try:
        transcription = transcribe_audio_with_assemblyai(audio_file_path)
        
        # Check if AssemblyAI succeeded
        if not transcription.startswith("Transcription failed") and not transcription.startswith("Audio transcription failed"):
            print("✓ AssemblyAI transcription successful")
            return transcription
        else:
            print("✗ AssemblyAI transcription failed")
            return transcription  # Return the error message from AssemblyAI
            
    except Exception as e:
        print(f"✗ AssemblyAI transcription error: {e}")
        return f"Audio transcription failed: {str(e)}"

def analyze_resume_with_gemini(resume_text):
    """Analyze resume using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Analyze the following resume and extract key information:
        
        Resume Content:
        {resume_text}
        
        Please provide a structured analysis including:
        1. Technical Skills
        2. Experience Level (Entry/Mid/Senior)
        3. Programming Languages
        4. Key Projects or Experience
        5. Recommended Interview Focus Areas
        
        Format the response as JSON with the following structure:
        {{
            "technical_skills": [],
            "experience_level": "",
            "programming_languages": [],
            "key_experience": [],
            "recommended_focus": []
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Clean and parse the JSON response
        parsed_response = clean_json_response(response.text)
        
        if parsed_response is None:
            # Return default structure if parsing fails
            parsed_response = {
                "technical_skills": ["Python", "JavaScript", "Web Development"],
                "experience_level": "Mid",
                "programming_languages": ["Python", "JavaScript"],
                "key_experience": ["Software Development", "Problem Solving"],
                "recommended_focus": ["Coding", "System Design"]
            }
        
        return json.dumps(parsed_response)
        
    except Exception as e:
        # Return default structure in case of error
        default_response = {
            "technical_skills": ["Programming", "Problem Solving"],
            "experience_level": "Mid",
            "programming_languages": ["Python"],
            "key_experience": ["Software Development"],
            "recommended_focus": ["Coding Fundamentals"]
        }
        print(f"Error analyzing resume with Gemini: {str(e)}")
        return json.dumps(default_response)

def generate_technical_questions(skills, experience_level, count=5):
    """Generate technical interview questions based on resume analysis"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Generate {count} technical interview questions for a candidate with:
        - Skills: {', '.join(skills)}
        - Experience Level: {experience_level}
        
        Questions should be appropriate for the experience level and cover:
        1. Coding problems
        2. System design (if applicable)
        3. Technical concepts
        4. Problem-solving scenarios
        
        Format as JSON array:
        [
            {{
                "question": "Question text",
                "type": "coding|system_design|concept|problem_solving",
                "difficulty": "easy|medium|hard",
                "expected_duration": "minutes"
            }}
        ]
        """
        
        response = model.generate_content(prompt)
        
        # Clean and parse the JSON response
        parsed_response = clean_json_response(response.text)
        
        if parsed_response is None:
            # Return default questions if parsing fails
            default_questions = [
                {
                    "question": "Explain the difference between a list and a tuple in Python.",
                    "type": "concept",
                    "difficulty": "easy",
                    "expected_duration": "5 minutes"
                },
                {
                    "question": "Write a function to reverse a string without using built-in methods.",
                    "type": "coding",
                    "difficulty": "medium",
                    "expected_duration": "15 minutes"
                },
                {
                    "question": "Design a simple URL shortening service like bit.ly.",
                    "type": "system_design",
                    "difficulty": "hard",
                    "expected_duration": "30 minutes"
                }
            ]
            parsed_response = default_questions[:count]
        
        return json.dumps(parsed_response)
        
    except Exception as e:
        # Return default questions in case of error
        default_questions = [
            {
                "question": "Describe your experience with the programming languages you know.",
                "type": "concept",
                "difficulty": "easy",
                "expected_duration": "10 minutes"
            },
            {
                "question": "How would you approach debugging a performance issue in an application?",
                "type": "problem_solving",
                "difficulty": "medium",
                "expected_duration": "15 minutes"
            }
        ]
        print(f"Error generating questions: {str(e)}")
        return json.dumps(default_questions[:count])

def analyze_interview_performance(questions, answers, duration):
    """Comprehensive analysis of interview performance"""
    try:
        # Calculate basic statistics
        questions_answered = len([a for a in answers if a and (a.get('text') or a.get('audio'))])
        total_text_length = sum([len(a.get('text', '')) for a in answers if a and a.get('text')])
        average_answer_length = total_text_length // max(questions_answered, 1)
        voice_answers_count = len([a for a in answers if a and a.get('method') == 'voice'])
        text_answers_count = len([a for a in answers if a and a.get('method') == 'text'])
        
        # Prepare prompt for Gemini analysis
        analysis_prompt = f"""
        Analyze this technical interview performance and provide a comprehensive report in JSON format.
        
        Interview Duration: {duration // 60} minutes {duration % 60} seconds
        Questions Answered: {questions_answered}/{len(questions)}
        Average Answer Length: {average_answer_length} characters
        Voice Answers: {voice_answers_count}
        Text Answers: {text_answers_count}
        
        Questions and Answers:
        """
        
        for i, (question, answer) in enumerate(zip(questions, answers)):
            q_text = question.get('question', question) if isinstance(question, dict) else str(question)
            a_text = answer.get('text', 'No answer provided') if answer else 'No answer provided'
            analysis_prompt += f"\nQ{i+1}: {q_text}\nA{i+1}: {a_text[:500]}...\n"
        
        analysis_prompt += """
        
        Please provide a JSON response with the following structure:
        {
            "overall_score": (integer 0-100),
            "performance_level": "excellent/good/satisfactory/needs_improvement",
            "strengths": [
                {"title": "Strength name", "description": "Detailed explanation"}
            ],
            "improvements": [
                {"title": "Area name", "description": "Specific suggestions"}
            ],
            "skill_scores": [
                {"name": "Technical Knowledge", "score": 85},
                {"name": "Problem Solving", "score": 75},
                {"name": "Communication", "score": 90},
                {"name": "Code Quality", "score": 80}
            ],
            "question_reviews": [
                {
                    "question": "Question text",
                    "answer": "Answer text (truncated)",
                    "quality": "excellent/good/fair/poor",
                    "feedback": "Specific feedback",
                    "method": "text/voice"
                }
            ],
            "recommendations": [
                {
                    "title": "Recommendation title",
                    "description": "Detailed recommendation",
                    "resources": [
                        {"title": "Resource name", "url": "https://example.com"}
                    ]
                }
            ]
        }
        
        Focus on:
        1. Technical accuracy and depth of answers
        2. Communication clarity and structure
        3. Problem-solving approach
        4. Use of examples and real-world experience
        5. Areas for improvement with specific actionable advice
        """
        
        # Get analysis from Gemini
        model = get_gemini_model('technical')
        response = model.generate_content(analysis_prompt)
        
        # Parse the response
        analysis_data = clean_json_response(response.text)
        
        if not analysis_data:
            # Fallback to basic analysis
            analysis_data = generate_basic_analysis(questions, answers, duration)
        
        # Add calculated statistics
        analysis_data.update({
            'questions_answered': questions_answered,
            'average_answer_length': average_answer_length,
            'voice_answers_count': voice_answers_count,
            'text_answers_count': text_answers_count
        })
        
        return analysis_data
        
    except Exception as e:
        print(f"Error in interview analysis: {e}")
        return generate_basic_analysis(questions, answers, duration)

def generate_basic_analysis(questions, answers, duration):
    """Generate basic fallback analysis"""
    questions_answered = len([a for a in answers if a and (a.get('text') or a.get('audio'))])
    completion_rate = (questions_answered / len(questions)) * 100 if questions else 0
    
    # Determine performance level based on completion rate
    if completion_rate >= 90:
        performance_level = "excellent"
        overall_score = 85
    elif completion_rate >= 70:
        performance_level = "good"
        overall_score = 75
    elif completion_rate >= 50:
        performance_level = "satisfactory"
        overall_score = 65
    else:
        performance_level = "needs_improvement"
        overall_score = 45
    
    return {
        "overall_score": overall_score,
        "performance_level": performance_level,
        "strengths": [
            {
                "title": "Interview Completion",
                "description": f"You completed {questions_answered} out of {len(questions)} questions."
            }
        ],
        "improvements": [
            {
                "title": "Answer Completeness",
                "description": "Focus on providing more detailed and comprehensive answers."
            }
        ],
        "skill_scores": [
            {"name": "Technical Knowledge", "score": overall_score},
            {"name": "Problem Solving", "score": max(40, overall_score - 10)},
            {"name": "Communication", "score": max(50, overall_score - 5)},
            {"name": "Preparation", "score": overall_score}
        ],
        "question_reviews": [
            {
                "question": q.get('question', str(q)) if isinstance(q, dict) else str(q),
                "answer": a.get('text', 'No answer') if a else 'No answer',
                "quality": "fair" if a and a.get('text') else "poor",
                "feedback": "Consider providing more detailed examples and technical depth.",
                "method": a.get('method', 'text') if a else 'text'
            }
            for i, (q, a) in enumerate(zip(questions, answers))
        ],
        "recommendations": [
            {
                "title": "Practice Technical Communication",
                "description": "Work on explaining technical concepts clearly and concisely.",
                "resources": [
                    {"title": "Interview Preparation Guide", "url": "#"},
                    {"title": "Technical Communication Tips", "url": "#"}
                ]
            }
        ],
        "questions_answered": questions_answered,
        "average_answer_length": 100,
        "voice_answers_count": len([a for a in answers if a and a.get('method') == 'voice']),
        "text_answers_count": len([a for a in answers if a and a.get('method') == 'text'])
    }