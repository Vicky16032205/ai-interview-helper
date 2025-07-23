# 🔒 Security Checklist for AI Interview Helper

## ✅ Pre-Deployment Security Checklist

### Environment Variables (CRITICAL)
- [ ] SECRET_KEY set in environment variables (never in code)
- [ ] GEMINI_API_KEY set in environment variables  
- [ ] ASSEMBLYAI_API_KEY set in environment variables
- [ ] All API keys removed from any config files
- [ ] .env files are in .gitignore
- [ ] No hardcoded passwords or tokens in code

### Django Security Settings
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS properly configured
- [ ] SECURE_SSL_REDIRECT=True
- [ ] SESSION_COOKIE_SECURE=True
- [ ] CSRF_COOKIE_SECURE=True
- [ ] SECURE_HSTS_SECONDS set (31536000)

### Database Security
- [ ] Database credentials in environment variables
- [ ] No database files committed to git (db.sqlite3)
- [ ] Production database has strong password

### File Upload Security
- [ ] Media files not committed to git
- [ ] File upload validation in place
- [ ] Resume files are private and not publicly accessible

### API Security
- [ ] Rate limiting on API endpoints
- [ ] Input validation on all forms
- [ ] CORS properly configured
- [ ] No sensitive data in API responses

### Monitoring & Logging
- [ ] Error logging configured
- [ ] No sensitive data in logs
- [ ] Log rotation set up

## 🚫 Never Commit These:
- .env files with real values
- API keys or secrets
- Database files
- User uploaded files (resumes, audio)
- SSL certificates or private keys
- Any file with passwords

## 📝 Safe to Commit:
- .env.example (with placeholder values)
- Code files
- Static assets (CSS, JS, images)
- Requirements files
- Documentation
- Configuration templates

## 🔍 Before Each Commit:
```bash
# Check for sensitive files
git status
git diff --cached

# Verify no secrets in staged files
grep -r "SECRET_KEY\|API_KEY\|PASSWORD" --include="*.py" .

# Run security check
python manage.py check --deploy
```

## 🚨 If You Accidentally Commit Secrets:
1. Immediately rotate/regenerate the compromised secrets
2. Remove the file from git history:
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch path/to/file' --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push to update remote repository
4. Update all instances with new secrets
