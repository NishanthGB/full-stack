# Quick Deployment Guide

Deploy your React frontend to Vercel and FastAPI backend to Render.

## 🚀 Quick Start

**See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete step-by-step instructions.**

## Prerequisites
- GitHub repository with your code
- [Vercel](https://vercel.com) account (free)
- [Render](https://render.com) account (free)
- [MongoDB Atlas](https://www.mongodb.com/atlas) (optional, free)

---

## 1. Database Setup (MongoDB Atlas)
1. Create a free cluster on MongoDB Atlas.
2. Create a database user (username/password).
3. Allow access from your app / Render's IPs or `0.0.0.0/0` for testing.
4. Copy the connection string (e.g. `mongodb+srv://<user>:<pw>@cluster0.mongodb.net/?retryWrites=true&w=majority`).

---

## 2. Backend Deployment (Render)
Recommended: use Render to host the FastAPI backend.

1. Push your code to GitHub.
2. In Render click **New +** -> **Web Service** and connect your repo.
3. Use the following settings (or use `render.yaml` in repo to create the service automatically):
   - **Name**: `video-sentiment-backend` (or your preferred name)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker backend.server:app --bind 0.0.0.0:$PORT`
4. Add Environment Variables in Render (Service > Environment):
   - `MONGO_URL` — your MongoDB connection string
   - `DB_NAME` — `video_sentiment` (optional)
   - `JWT_SECRET_KEY` — strong secret for signing tokens
   - `CORS_ORIGINS` — a comma-separated list of allowed origins (e.g. `https://your-frontend.vercel.app` or `*` for testing)
5. Deploy — Render will run the build and start commands.

Notes:
- The backend loads `backend/.env` for local development; in production set env vars in Render.
- We added a `Procfile` and `gunicorn` to `backend/requirements.txt` so the app can be run with Gunicorn + Uvicorn workers.

---

## 3. Frontend Deployment (Vercel)
Recommended: deploy the React app to Vercel.

1. In Vercel click **Add New** -> **Project** and import the GitHub repo.
2. In the import settings set the project root to the repo root (Vercel will use the `vercel.json` included in this repo which builds the `frontend` app).
3. Vercel will run the `build` script from `frontend/package.json` (`craco build`).
4. In Vercel > Settings > Environment Variables add:
   - `REACT_APP_BACKEND_URL` — set to your Render backend base URL (for example `https://video-sentiment-backend.onrender.com/api`)
   - Any other frontend-specific variables (`REACT_APP_ENABLE_VISUAL_EDITS`, etc.)
5. Deploy — Vercel will produce a static site that calls your backend.

Notes:
- The frontend reads `REACT_APP_BACKEND_URL` in several files. Make sure it points to the live backend.

---

## 4. Local testing
Backend (local):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000
```

Frontend (local):

```powershell
cd frontend
npm install
npm run start
```

When testing locally, set `REACT_APP_BACKEND_URL` in `.env` file inside `frontend` (create `.env` with `REACT_APP_BACKEND_URL=http://localhost:8000/api`).

---

## 5. What I changed to help deployment
- Added `vercel.json` to build the `frontend` folder on Vercel.
- Added `render.yaml` sample to help create the backend service on Render.
- Added `backend/Procfile` and appended `gunicorn` to `backend/requirements.txt` so the backend can be started with Gunicorn + Uvicorn workers.
- Updated this `deployment.md` with corrected paths and commands.

If you want, I can also:
- Create a small health-check endpoint and a static `index.html` fallback for the frontend.
- Add CI (GitHub Actions) to run tests and deploy automatically.
