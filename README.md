# AI Interview Helper

A comprehensive Django-based web application designed to help job seekers practice and improve their interview skills using AI-powered feedback and evaluation.

## Features

### 🎯 HR Interview Practice
- Common HR interview questions
- Text and audio response options
- AI-powered feedback and evaluation
- Follow-up questions based on responses
- STAR method guidance for behavioral questions

### 💻 Technical Interview Practice
- Coding challenges and technical questions
- Real-time code evaluation
- Multiple programming language support
- Difficulty-based question selection

### 🧠 DSA (Data Structures & Algorithms) Practice
- Curated DSA problems
- Step-by-step solutions
- Complexity analysis
- Practice tracking

## Technology Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite (development)
- **AI Integration**: Google AI/ML services
- **Audio Processing**: Web Audio API
- **Containerization**: Docker

## Installation

### Prerequisites
- Python 3.8+
- pip
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai_interview_helper.git
   cd ai_interview_helper
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Load sample data**
   ```bash
   python manage.py load_sample_questions
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

## Project Structure

```
ai_interview_helper/
├── ai_interview_helper/        # Django project settings
├── apps/
│   ├── core/                   # Core application (homepage)
│   ├── dsa/                    # DSA practice module
│   └── interview/              # Interview practice module
├── static/                     # Static files (CSS, JS, images)
├── templates/                  # HTML templates
├── media/                      # User uploads
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
└── docker-compose.yml          # Docker configuration
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

### Google AI Services Setup

1. Create a Google Cloud Project
2. Enable the required AI/ML APIs
3. Create service account credentials
4. Download the credentials JSON file
5. Set the path in your environment variables

## Usage

### HR Interview Practice
1. Navigate to the HR Interview section
2. Select a question from the predefined list
3. Choose between text or audio response
4. Submit your answer for AI evaluation
5. Review feedback and suggestions
6. Answer follow-up questions if provided

### Technical Interview Practice
1. Go to the Technical Interview section
2. Select your preferred programming language
3. Choose difficulty level
4. Solve coding problems
5. Get instant feedback on your solutions

### DSA Practice
1. Access the DSA Practice section
2. Browse problems by category or difficulty
3. Read problem statements and constraints
4. Practice implementing solutions
5. Review optimal approaches and explanations

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who helped improve this project
- Inspired by the need to democratize interview preparation
- Built with love for the developer community

## Support

If you encounter any issues or have questions, please:
1. Check the [Issues](https://github.com/yourusername/ai_interview_helper/issues) page
2. Create a new issue if your problem isn't already documented
3. Provide detailed information about your environment and the issue

---

**Happy Interview Preparation! 🚀**
