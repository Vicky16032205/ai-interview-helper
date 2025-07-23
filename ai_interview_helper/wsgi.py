"""
WSGI config for ai_interview_helper project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use Render settings in production, fallback to default settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_interview_helper.settings_render')

application = get_wsgi_application()