# 🚀 Complete Deployment Guide

This guide will help you deploy your fullstack video sentiment analysis application to Vercel (frontend) and Render (backend).

## 📋 Prerequisites

- GitHub account with your code repository
- [Vercel](https://vercel.com) account (free tier available)
- [Render](https://render.com) account (free tier available)
- MongoDB Atlas account (optional, free tier available)

## 🎯 Architecture Overview

```
┌─────────────────┐    API calls    ┌─────────────────┐    DB queries    ┌─────────────────┐
│   Frontend      │────────────────▶│    Backend      │─────────────────▶│    Database     │
│   (Vercel)      │                 │   (Render)      │                  │  (MongoDB)      │
│   React + CRA   │                 │ FastAPI + Python│                  │   or MockDB     │
└─────────────────┘                 └─────────────────┘                  └─────────────────┘
```

---

## 🌍 Step 1: Push Code to GitHub

1. Create a new repository on GitHub
2. Push your entire project to GitHub:
```bash
git init
git add .
git commit -m "Initial commit - fullstack video app"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

---

## 🎨 Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Project
1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New"** → **"Project"**
3. Select your GitHub repository
4. **Import the project**

### 2.2 Configure Build Settings
Vercel should auto-detect it as a React app, but verify these settings:

- **Framework Preset**: `Create React App`
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `build` (auto-detected)
- **Install Command**: `npm install` (auto-detected)

The included `vercel.json` will ensure Vercel builds the frontend correctly.

### 2.3 Environment Variables
In Vercel dashboard → Your Project → Settings → Environment Variables, add:

| Variable | Value | Notes |
|----------|--------|--------|
| `REACT_APP_BACKEND_URL` | `https://your-backend-name.onrender.com` | Replace with your Render backend URL |
| `REACT_APP_ENABLE_VISUAL_EDITS` | `false` | Optional |

### 2.4 Deploy
Click **"Deploy"** - Vercel will:
1. Install dependencies with `npm install`
2. Build with `npm run build` 
3. Deploy the static files
4. Provide you with a live URL like `https://your-app.vercel.app`

---

## 🔧 Step 3: Deploy Backend to Render

### 3.1 Create Render Web Service
1. Go to [render.com](https://render.com) and sign in with GitHub
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

### 3.2 Service Configuration
- **Name**: `video-sentiment-backend` (or your choice)
- **Environment**: `Python 3`
- **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT`

### 3.3 Environment Variables
In Render dashboard → Your Service → Environment, add:

| Variable | Value | Example | Required |
|----------|--------|---------|----------|
| `MONGO_URL` | Your MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` | No* |
| `DB_NAME` | Database name | `video_sentiment` | No |
| `JWT_SECRET_KEY` | Strong random string | `your-super-secret-key-here` | Yes |
| `CORS_ORIGINS` | Your Vercel frontend URL | `https://your-app.vercel.app` | Yes |
| `PYTHON_VERSION` | `3.11` | `3.11` | No |

*If `MONGO_URL` is not provided, the app will use in-memory MockDB (data lost on restart).

### 3.4 Deploy Backend
Click **"Create Web Service"** - Render will:
1. Clone your repository
2. Install Python dependencies
3. Start your FastAPI server
4. Provide a URL like `https://video-sentiment-backend.onrender.com`

---

## 🗄️ Step 4: Setup Database (Optional)

### 4.1 MongoDB Atlas (Recommended)
1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a free cluster
3. Create a database user
4. Add your IP to Network Access (or `0.0.0.0/0` for all)
5. Get connection string and add to Render environment variables

### 4.2 Alternative: Use MockDB
If you don't set `MONGO_URL`, the app uses in-memory storage:
- ✅ **Pros**: Simple, no setup required
- ❌ **Cons**: Data lost on server restart

---

## 🔄 Step 5: Connect Frontend to Backend

### 5.1 Update Frontend Environment Variable
1. Get your Render backend URL (e.g., `https://video-sentiment-backend.onrender.com`)
2. In Vercel → Settings → Environment Variables
3. Update `REACT_APP_BACKEND_URL` to your backend URL
4. Redeploy frontend (Vercel will auto-redeploy)

### 5.2 Update Backend CORS
1. In Render → Environment Variables
2. Set `CORS_ORIGINS` to your Vercel frontend URL
3. Render will auto-redeploy backend

---

## 🧪 Step 6: Test Your Deployment

### 6.1 Test Frontend
1. Visit your Vercel URL
2. Try to register/login
3. Check browser console for errors

### 6.2 Test Backend
1. Visit `https://your-backend.onrender.com/docs`
2. You should see FastAPI documentation
3. Test API endpoints

### 6.3 Test Connection
1. Register a new user on frontend
2. Upload a test video
3. Check if everything works end-to-end

---

## 🚨 Troubleshooting

### Frontend Issues
| Problem | Solution |
|---------|----------|
| Build fails | Check `package.json` dependencies, try `npm install --legacy-peer-deps` |
| "Failed to fetch" errors | Check `REACT_APP_BACKEND_URL` environment variable |
| 404 errors | Ensure `vercel.json` is in root directory |

### Backend Issues
| Problem | Solution |
|---------|----------|
| Build fails | Check `requirements.txt`, ensure all dependencies listed |
| Server won't start | Check start command: `gunicorn -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT` |
| CORS errors | Check `CORS_ORIGINS` environment variable matches frontend URL |
| Database errors | Verify `MONGO_URL` connection string or check MockDB fallback |

### Common Issues
- **Render free tier**: Service may sleep after 15 minutes of inactivity (first request will be slow)
- **Environment variables**: Changes require service restart/redeploy
- **Case sensitivity**: Linux deployment is case-sensitive (unlike Windows development)

---

## 📱 Production Checklist

### Before Going Live
- [ ] Set strong `JWT_SECRET_KEY` 
- [ ] Configure proper `CORS_ORIGINS` (no wildcards in production)
- [ ] Setup MongoDB Atlas for data persistence
- [ ] Test all user flows (register, login, upload, stream)
- [ ] Check error handling and loading states
- [ ] Verify mobile responsiveness

### Performance Optimization
- [ ] Enable Render auto-scaling (paid plans)
- [ ] Setup CDN for video files (AWS S3 + CloudFront)
- [ ] Add database indexing for better query performance
- [ ] Implement proper logging and monitoring

---

## 🎉 Success!

Your application is now live:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.onrender.com`
- **API Docs**: `https://your-backend.onrender.com/docs`

## 🔄 Automatic Deployments

Both Vercel and Render will automatically redeploy when you push to your GitHub repository's main branch.

## 💡 Next Steps

- Setup custom domains
- Add monitoring and analytics  
- Implement CI/CD with GitHub Actions
- Add automated testing
- Setup staging environments