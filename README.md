# 🤖 AI Interview Helper

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-5.0.1-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

AI-powered interview preparation platform built with Django and Google Gemini AI. Practice HR interviews, technical coding challenges, and DSA problems with intelligent feedback.

## ✨ Features

- **HR Interview Practice**: 200+ questions with text/audio responses and AI feedback
- **Technical Interviews**: Coding challenges with real-time evaluation
- **DSA Practice**: 500+ curated problems with LeetCode integration
- **AI-Powered Evaluation**: Intelligent feedback using Google Gemini AI
- **Progress Tracking**: Monitor your improvement over time
- **Audio Recording**: Voice response capabilities for realistic practice

## 🛠 Tech Stack

- **Backend**: Django 5.0.1, Python 3.8+
- **AI**: Google Gemini AI, AssemblyAI
- **Frontend**: Bootstrap, JavaScript, Web Audio API
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Deployment**: Docker, Gunicorn, WhiteNoise

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- Google Gemini API key (for AI features)

### Installation

1. **Clone and setup**
   ```bash
   git clone https://github.com/Vicky16032205/ai-interview-helper.git
   cd ai-interview-helper
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env  # macOS/Linux
   ```
   Edit `.env` and add your API keys:
   ```env
   SECRET_KEY=your-secret-key
   GEMINI_API_KEY=your-gemini-api-key
   DEBUG=True
   ```

4. **Setup database**
   ```bash
   python manage_dev.py migrate  # For development
   python manage_dev.py load_sample_questions
   python manage_dev.py createsuperuser  # optional
   ```

5. **Run the application**
   ```bash
   python manage_dev.py runserver  # For development
   ```
   
   Visit `http://localhost:8000` to start practicing!

### Docker Setup (Alternative)
```bash
git clone https://github.com/Vicky16032205/ai-interview-helper.git
cd ai-interview-helper
cp .env.example .env  # Edit with your API keys
docker-compose up --build
```

## ⚙️ Configuration

Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/) and add it to your `.env` file:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
GEMINI_API_KEY=your-gemini-api-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 📁 Project Structure

```
ai_interview_helper/
├── ai_interview_helper/    # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI config
│   └── asgi.py            # ASGI config
├── apps/                  # Django applications
│   ├── core/              # Homepage and navigation
│   ├── dsa/               # DSA practice module
│   └── interview/         # Interview practice module
├── static/                # Static files
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images and icons
├── templates/             # HTML templates
├── media/                 # User uploads (audio, resumes)
├── .env.example           # Environment variables template
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Docker image setup
├── requirements.txt       # Python dependencies
├── manage.py              # Django management script
└── db.sqlite3             # SQLite database
```

## 🎯 Usage

1. **DSA Practice**: Browse problems by category/difficulty, solve with AI feedback
2. **HR Interview**: Practice with text/audio responses, get STAR method guidance
3. **Technical Interview**: Code challenges with real-time evaluation
4. **Progress Tracking**: Monitor improvement and identify weak areas

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature-name`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature-name`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Vicky16032205/ai-interview-helper/issues)
- **Documentation**: Check this README for setup help
- **Community**: [GitHub Discussions](https://github.com/Vicky16032205/ai-interview-helper/discussions)

---

<div align="center">

**Happy Interview Preparation! 🚀**

[![GitHub stars](https://img.shields.io/github/stars/Vicky16032205/ai-interview-helper?style=social)](https://github.com/Vicky16032205/ai-interview-helper/stargazers)

</div>
