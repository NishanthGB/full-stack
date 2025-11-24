# 🚨 Deployment Troubleshooting Guide

## Backend Deployment Issues (Render)

### ❌ Error: `ModuleNotFoundError: No module named 'app'`

**Cause**: Render is looking for `app.py` but your file is `server.py`

**✅ Solution**: Updated configuration files:
- `render.yaml`: Changed from `backend.server:app` to `server:app`
- `backend/Procfile`: Fixed module path for correct directory structure

### ❌ Error: `No module named 'backend'`

**Cause**: Render sets root directory to `backend`, so imports should be relative

**✅ Solution**: 
- Build command: `pip install -r requirements.txt` (not `backend/requirements.txt`)
- Start command: `gunicorn server:app` (not `backend.server:app`)

### 🔧 Render Deployment Steps:

**CRITICAL**: The current deployment is using wrong start command. Follow these exact steps:

1. **Delete Current Failed Service** (if exists):
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Delete the existing `fullstack-backend` service that's failing

2. **Create New Web Service**:
   - Click "New" → "Web Service"  
   - Connect GitHub repository: `NishanthGB/full-stack`

3. **Configure Service Settings** (EXACT VALUES):
   ```
   Name: fullstack-backend
   Root Directory: backend
   Environment: Python 3.11
   Plan: Free (or Starter)
   Region: Oregon (or closest to you)
   
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT --timeout 120
   ```

4. **Environment Variables**:
   ```
   PYTHON_VERSION=3.11
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

5. **Deploy**: Click "Create Web Service"

### ⚠️ **IMPORTANT**: 
If Render still shows `gunicorn app:app` in logs, it means the manual dashboard settings override the `render.yaml`. Always check the **Start Command** field in the dashboard matches exactly:
```
gunicorn -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT --timeout 120
```

---

## Frontend Deployment Issues (Vercel)

### 🔧 Vercel Deployment Steps:

1. **Import Project**:
   - Go to [Vercel Dashboard](https://vercel.com/new)
   - Import `NishanthGB/full-stack`
   - Set **Root Directory**: `frontend`

2. **Build Settings**:
   ```
   Framework: Create React App
   Build Command: npm run build
   Output Directory: build
   Install Command: npm install
   ```

3. **Environment Variables**:
   ```
   REACT_APP_BACKEND_URL=https://your-backend.onrender.com
   REACT_APP_ENABLE_VISUAL_EDITS=false
   ENABLE_HEALTH_CHECK=true
   NODE_ENV=production
   ```

---

## 🔗 Connecting Frontend & Backend

### Step 1: Deploy Backend First
1. Deploy backend to Render
2. Copy the Render URL (e.g., `https://fullstack-backend-xyz.onrender.com`)

### Step 2: Configure Frontend
1. In Vercel dashboard → Environment Variables
2. Set `REACT_APP_BACKEND_URL` to your Render backend URL
3. Redeploy frontend

### Step 3: Configure Backend CORS
1. In Render dashboard → Environment Variables  
2. Set `FRONTEND_URL` to your Vercel frontend URL
3. Backend will automatically restart

---

## 🐛 Common Issues & Solutions

### Issue: "Network Error" in Frontend
**Cause**: Backend URL not configured or incorrect
**Solution**: 
- Check `REACT_APP_BACKEND_URL` in Vercel environment variables
- Ensure backend is deployed and running on Render
- Test backend API directly: `https://your-backend.onrender.com/docs`

### Issue: CORS Errors
**Cause**: Frontend URL not whitelisted in backend
**Solution**:
- Set `FRONTEND_URL` environment variable in Render
- Check backend logs for CORS configuration

### Issue: Build Fails on Vercel
**Cause**: Missing dependencies or build configuration
**Solution**:
- Ensure `frontend/package.json` exists
- Check build logs for specific errors
- Verify Node.js version compatibility

### Issue: Backend Crashes on Render
**Cause**: Missing dependencies or startup errors
**Solution**:
- Check `backend/requirements.txt` includes all dependencies
- Review Render logs for specific Python errors
- Ensure `server.py` has correct FastAPI app export

---

## 📊 Deployment Checklist

### Backend (Render):
- ✅ `render.yaml` configured correctly
- ✅ `backend/Procfile` uses correct module path
- ✅ `backend/requirements.txt` includes all dependencies
- ✅ Environment variables set (`PYTHON_VERSION`, `FRONTEND_URL`)
- ✅ Service deployed and running

### Frontend (Vercel):
- ✅ Root directory set to `frontend`
- ✅ Build settings configured for Create React App
- ✅ Environment variables set (`REACT_APP_BACKEND_URL`)
- ✅ Deployment successful and accessible

### Integration:
- ✅ Frontend can call backend API
- ✅ CORS configured properly
- ✅ WebSocket connections working
- ✅ File uploads functioning

---

## 📞 Support Resources

- [Render Deployment Docs](https://render.com/docs/web-services)
- [Vercel Deployment Guide](https://vercel.com/docs/deployments)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Create React App Deployment](https://create-react-app.dev/docs/deployment/)

Your deployment configurations have been fixed! Try deploying again with the corrected settings.