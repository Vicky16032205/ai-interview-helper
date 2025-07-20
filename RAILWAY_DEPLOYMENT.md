# 🚂 Railway Deployment Guide for AI Interview Helper

## Prerequisites
1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **API Keys**: Get your Gemini API and AssemblyAI API keys ready

## Step-by-Step Deployment

### 1. **Push to GitHub** (if not already done)
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. **Deploy on Railway**
1. Go to [railway.app](https://railway.app) and sign in
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `ai-interview-helper` repository
5. Railway will automatically detect it's a Python/Django project

### 3. **Configure Environment Variables**
In your Railway project dashboard:
1. Go to "Variables" tab
2. Add these environment variables:

**Required Variables:**
```
DJANGO_SETTINGS_MODULE=ai_interview_helper.settings_railway
SECRET_KEY=your-super-secure-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
ASSEMBLYAI_API_KEY=your-assemblyai-api-key
```

**Optional Variables:**
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
GEMINI_HR_API_KEY=your-gemini-hr-key
ADMIN_EMAIL=admin@yourdomain.com
```

### 4. **Add PostgreSQL Database** (Recommended)
1. In Railway dashboard, click "Add Service"
2. Select "PostgreSQL"
3. Railway will automatically set the `DATABASE_URL` variable

### 5. **Deploy and Test**
1. Railway will automatically build and deploy
2. Once deployed, visit your app URL (shown in Railway dashboard)
3. Test the health check: `https://your-app.railway.app/health/`

### 6. **Create Admin User**
In Railway dashboard terminal:
```bash
python manage.py createsuperuser
```

## Getting Your API Keys

### Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key and add to Railway environment variables

### AssemblyAI API Key
1. Visit [AssemblyAI](https://www.assemblyai.com/)
2. Sign up for free account
3. Go to dashboard and copy your API key
4. Add to Railway environment variables

## Troubleshooting

### Common Issues:
1. **Build Fails**: Check requirements.txt format
2. **Database Errors**: Ensure PostgreSQL is added and DATABASE_URL is set
3. **Static Files Not Loading**: Railway handles this automatically with WhiteNoise
4. **API Errors**: Verify your API keys are correctly set

### Railway CLI (Optional)
Install Railway CLI for easier management:
```bash
npm install -g @railway/cli
railway login
railway link  # In your project directory
railway logs  # View application logs
```

## Post-Deployment Checklist
- [ ] App loads without errors
- [ ] Health check returns 200: `/health/`
- [ ] Admin panel works: `/admin/`
- [ ] Technical interview generates questions
- [ ] HR interview works with audio
- [ ] DSA questions load properly
- [ ] Email forms work (if configured)

## Performance Tips
- Railway provides automatic scaling
- Monitor usage in Railway dashboard
- Consider upgrading plan for production use
- Set up custom domain in Railway settings

Your AI Interview Helper should now be live! 🎉
