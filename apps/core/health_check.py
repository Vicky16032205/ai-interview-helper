from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.conf import settings
import os

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for production monitoring"""
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check critical environment variables
        critical_vars = ['GEMINI_API_KEY', 'ASSEMBLYAI_API_KEY']
        missing_vars = [var for var in critical_vars if not os.environ.get(var)]
        
        status = "healthy"
        issues = []
        
        if missing_vars:
            status = "degraded"
            issues.append(f"Missing environment variables: {', '.join(missing_vars)}")
        
        # Check media directory
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            issues.append("Media directory not accessible")
            status = "degraded"
        
        response_data = {
            "status": status,
            "version": "1.0.0",
            "database": "connected",
            "issues": issues if issues else None
        }
        
        status_code = 200 if status == "healthy" else 503
        return JsonResponse(response_data, status=status_code)
        
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status=503)
