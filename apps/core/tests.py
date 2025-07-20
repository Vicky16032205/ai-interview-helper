import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.interview.models import InterviewSession, InterviewQuestion

class CoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_index_page_loads(self):
        """Test that the homepage loads successfully"""
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Interview Helper')

    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get(reverse('core:health_check'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertIn('database', data)

    def test_progress_page_authenticated(self):
        """Test progress page for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:progress'))
        self.assertEqual(response.status_code, 200)

    def test_submit_review(self):
        """Test review submission"""
        review_data = {
            'reviewer_name': 'Test User',
            'reviewer_email': 'test@example.com',
            'rating': '5',
            'review_message': 'Great application!'
        }
        response = self.client.post(
            reverse('core:submit_review'), 
            review_data
        )
        self.assertEqual(response.status_code, 200)


class InterviewModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_interview_session_creation(self):
        """Test creating an interview session"""
        session = InterviewSession.objects.create(
            user=self.user,
            interview_type='technical'
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.interview_type, 'technical')

    def test_interview_question_creation(self):
        """Test creating an interview question"""
        session = InterviewSession.objects.create(
            user=self.user,
            interview_type='hr'
        )
        question = InterviewQuestion.objects.create(
            session=session,
            question="Tell me about yourself",
            answer="I am a software developer"
        )
        self.assertEqual(question.session, session)
        self.assertEqual(question.question, "Tell me about yourself")


class SecurityTest(TestCase):
    def test_csrf_protection(self):
        """Test CSRF protection is enabled"""
        from django.conf import settings
        self.assertIn('django.middleware.csrf.CsrfViewMiddleware', settings.MIDDLEWARE)

    def test_security_middleware(self):
        """Test security middleware is configured"""
        from django.conf import settings
        self.assertIn('django.middleware.security.SecurityMiddleware', settings.MIDDLEWARE)
        
    def test_debug_false_in_production(self):
        """Ensure DEBUG is False in production settings"""
        import os
        if os.environ.get('DJANGO_SETTINGS_MODULE') == 'ai_interview_helper.settings_production':
            from django.conf import settings
            self.assertFalse(settings.DEBUG)
