# 🚀 Fresh Deployment Guide

## 🎯 Project Overview

This is a full-stack video sentiment analysis application:
- **Frontend**: React with modern UI components
- **Backend**: FastAPI with JWT authentication
- **Database**: MongoDB (with in-memory fallback)
- **Features**: Video upload, processing, streaming, user management

---

## 📋 Pre-Deployment Checklist

✅ **Code is clean** - No hardcoded URLs  
✅ **Frontend builds successfully** - Tested locally  
✅ **Backend has all dependencies** - requirements.txt updated  
✅ **Environment variables configured** - For both platforms  
✅ **CORS setup** - For cross-origin requests  

---

## 🏗️ Step 1: Deploy Backend to Render

### 1.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your GitHub account

### 1.2 Create Web Service
1. Click **"New"** → **"Web Service"**
2. Connect repository: `NishanthGB/full-stack`
3. Configure service settings:

```
Name: fullstack-backend
Root Directory: backend
Environment: Python 3.11
Plan: Free
Region: Oregon (or closest to you)

Build Command: pip install -r requirements.txt
Start Command: gunicorn -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT --timeout 120
```

### 1.3 Add Environment Variables
In Render dashboard → Environment tab, add:

```
PYTHON_VERSION = 3.11
JWT_SECRET_KEY = your-super-secret-jwt-key-change-this
FRONTEND_URL = https://full-stack-git-main-nishanthgbs-projects.vercel.app
```

**❗ Important**: Replace with your actual Vercel URL after Step 2

### 1.4 Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Copy your backend URL (e.g., `https://fullstack-backend-xyz.onrender.com`)

---

## 🌐 Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Account  
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub account
3. Connect your GitHub account

### 2.2 Import Project
1. Click **"Add New..."** → **"Project"**
2. Import `NishanthGB/full-stack` repository
3. Configure project settings:

```
Project Name: fullstack-frontend
Root Directory: frontend
Framework: Create React App
Build Command: npm run build
Output Directory: build
Install Command: npm install
```

### 2.3 Add Environment Variables
In Vercel dashboard → Settings → Environment Variables:

```
REACT_APP_BACKEND_URL = https://your-backend.onrender.com
REACT_APP_ENABLE_VISUAL_EDITS = false
ENABLE_HEALTH_CHECK = true
NODE_ENV = production
```

**Replace `your-backend.onrender.com` with your actual Render URL from Step 1.4**

### 2.4 Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes for deployment
3. Copy your frontend URL (e.g., `https://fullstack-frontend.vercel.app`)

---

## 🔗 Step 3: Connect Frontend & Backend

### 3.1 Update Backend CORS
1. Go back to Render dashboard
2. Your backend service → Environment tab
3. Update `FRONTEND_URL` with your Vercel URL from Step 2.4
4. Save (backend will auto-restart)

### 3.2 Test Connection
1. Visit your Vercel frontend URL
2. Try registering a new account
3. Check browser console for any errors
4. Test video upload functionality

---

## 🧪 Step 4: Verify Deployment

### 4.1 Backend Health Check
Visit: `https://your-backend.onrender.com/docs`
- Should show FastAPI documentation
- Try the `/api/auth/register` endpoint

### 4.2 Frontend Functionality
Visit: `https://your-frontend.vercel.app`
- Login/Register should work
- Dashboard should load
- Video upload should function

### 4.3 Integration Test
1. Register a new account
2. Upload a test video
3. Check if processing works
4. Verify streaming functionality

---

## 🔧 Troubleshooting

### Frontend Issues

**Build Fails on Vercel:**
- Check Node.js version compatibility
- Ensure all dependencies in package.json
- Check build logs for specific errors

**API Calls Fail:**
- Verify `REACT_APP_BACKEND_URL` is set correctly
- Check browser network tab for 404/CORS errors
- Ensure backend is deployed and running

### Backend Issues

**Build Fails on Render:**
- Check Python version (should be 3.11+)
- Verify all dependencies in requirements.txt
- Check Render build logs

**Server Won't Start:**
- Verify start command is exactly: `gunicorn -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT --timeout 120`
- Check if `server.py` exists in backend directory
- Review Render runtime logs

### CORS Errors

**"Access blocked by CORS policy":**
- Check `FRONTEND_URL` is set in Render environment
- Ensure no trailing slash in URLs
- Verify backend is receiving the correct origin header

---

## 📊 Final URLs

After successful deployment, you should have:

- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.onrender.com`
- **API Docs**: `https://your-backend.onrender.com/docs`

---

## 🚨 Important Notes

1. **Free Tier Limitations**: Render free tier goes to sleep after 15 minutes of inactivity
2. **Cold Start**: First request after sleep may take 30-60 seconds
3. **Environment Variables**: Always set in platform dashboards, not in code
4. **HTTPS Only**: Both platforms use HTTPS, ensure your code handles this correctly
5. **Domain Updates**: If you change domains, update CORS settings immediately

---

## 📞 Support

If you encounter issues:
1. Check platform status pages (status.render.com, vercel-status.com)
2. Review deployment logs in respective dashboards  
3. Test API endpoints directly using browser/Postman
4. Verify environment variables are set correctly

**Happy Deploying! 🎉**