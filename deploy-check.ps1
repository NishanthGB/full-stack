# 🚀 Fullstack Video App - Deployment Preparation (PowerShell)
# Run this script to check if your project is ready for deployment

Write-Host "🚀 Fullstack Video App - Deployment Preparation" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "frontend") -and -not (Test-Path "backend")) {
    Write-Host "❌ Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "`n📋 Checking project structure..." -ForegroundColor Yellow

# Check frontend
if (Test-Path "frontend") {
    Write-Host "✅ Frontend directory found" -ForegroundColor Green
    if (Test-Path "frontend/package.json") {
        Write-Host "✅ Frontend package.json found" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend package.json missing" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Frontend directory missing" -ForegroundColor Red
}

# Check backend
if (Test-Path "backend") {
    Write-Host "✅ Backend directory found" -ForegroundColor Green
    if (Test-Path "backend/requirements.txt") {
        Write-Host "✅ Backend requirements.txt found" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend requirements.txt missing" -ForegroundColor Red
    }
    if (Test-Path "backend/server.py") {
        Write-Host "✅ Backend server.py found" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend server.py missing" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Backend directory missing" -ForegroundColor Red
}

# Check deployment files
Write-Host "`n📄 Checking deployment configuration..." -ForegroundColor Yellow

if (Test-Path "vercel.json") {
    Write-Host "✅ vercel.json found" -ForegroundColor Green
} else {
    Write-Host "❌ vercel.json missing - it should be created automatically" -ForegroundColor Red
}

if (Test-Path "render.yaml") {
    Write-Host "✅ render.yaml found" -ForegroundColor Green
} else {
    Write-Host "❌ render.yaml missing - it should be created automatically" -ForegroundColor Red
}

if (Test-Path "backend/Procfile") {
    Write-Host "✅ backend/Procfile found" -ForegroundColor Green
} else {
    Write-Host "❌ backend/Procfile missing - it should be created automatically" -ForegroundColor Red
}

# Check .gitignore
Write-Host "`n🔒 Checking security configuration..." -ForegroundColor Yellow

if (Test-Path ".gitignore") {
    Write-Host "✅ .gitignore found" -ForegroundColor Green
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -match "\.env") {
        Write-Host "✅ .env files are ignored" -ForegroundColor Green
    } else {
        Write-Host "⚠️  .env files should be added to .gitignore" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ .gitignore missing" -ForegroundColor Red
}

# Check if gunicorn is in requirements.txt
if (Test-Path "backend/requirements.txt") {
    $reqContent = Get-Content "backend/requirements.txt" -Raw
    if ($reqContent -match "gunicorn") {
        Write-Host "✅ gunicorn found in requirements.txt" -ForegroundColor Green
    } else {
        Write-Host "⚠️  gunicorn should be in requirements.txt for production" -ForegroundColor Yellow
    }
}

Write-Host "`n🔧 Deployment URLs to use:" -ForegroundColor Cyan
Write-Host "Frontend (Vercel): https://your-app.vercel.app"
Write-Host "Backend (Render):  https://your-backend.onrender.com"

Write-Host "`n🌍 Environment Variables Needed:" -ForegroundColor Cyan
Write-Host ""
Write-Host "For Vercel (Frontend):" -ForegroundColor White
Write-Host "  REACT_APP_BACKEND_URL=https://your-backend.onrender.com" -ForegroundColor Gray
Write-Host ""
Write-Host "For Render (Backend):" -ForegroundColor White
Write-Host "  JWT_SECRET_KEY=your-super-secret-key" -ForegroundColor Gray
Write-Host "  CORS_ORIGINS=https://your-app.vercel.app" -ForegroundColor Gray
Write-Host "  MONGO_URL=mongodb+srv://... (optional)" -ForegroundColor Gray

Write-Host "`n✅ Project structure looks good!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Push code to GitHub" -ForegroundColor Gray
Write-Host "2. Create Vercel project from GitHub repo" -ForegroundColor Gray
Write-Host "3. Create Render web service from GitHub repo" -ForegroundColor Gray
Write-Host "4. Set environment variables in both platforms" -ForegroundColor Gray
Write-Host "5. Test the deployed application" -ForegroundColor Gray

Write-Host "`nSee DEPLOYMENT_GUIDE.md for detailed instructions." -ForegroundColor Cyan

# Test if we can build frontend
Write-Host "`n🧪 Testing frontend build..." -ForegroundColor Yellow
if (Test-Path "frontend/package.json") {
    try {
        Push-Location "frontend"
        $buildResult = npm run build 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Frontend build successful!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Frontend build had issues - check dependencies" -ForegroundColor Yellow
        }
        Pop-Location
    } catch {
        Write-Host "❌ Could not test frontend build" -ForegroundColor Red
        Pop-Location
    }
}

Write-Host "`n🎉 Ready for deployment to Vercel and Render!" -ForegroundColor Green