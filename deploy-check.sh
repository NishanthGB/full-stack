#!/bin/bash
# 🚀 Deployment Helper Script
# This script helps prepare your project for deployment

echo "🚀 Fullstack Video App - Deployment Preparation"
echo "=============================================="

# Check if we're in the right directory
if [[ ! -f "package.json" && ! -d "frontend" && ! -d "backend" ]]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📋 Checking project structure..."

# Check frontend
if [ -d "frontend" ]; then
    echo "✅ Frontend directory found"
    if [ -f "frontend/package.json" ]; then
        echo "✅ Frontend package.json found"
    else
        echo "❌ Frontend package.json missing"
    fi
else
    echo "❌ Frontend directory missing"
fi

# Check backend
if [ -d "backend" ]; then
    echo "✅ Backend directory found"
    if [ -f "backend/requirements.txt" ]; then
        echo "✅ Backend requirements.txt found"
    else
        echo "❌ Backend requirements.txt missing"
    fi
    if [ -f "backend/server.py" ]; then
        echo "✅ Backend server.py found"
    else
        echo "❌ Backend server.py missing"
    fi
else
    echo "❌ Backend directory missing"
fi

# Check deployment files
echo -e "\n📄 Checking deployment configuration..."

if [ -f "vercel.json" ]; then
    echo "✅ vercel.json found"
else
    echo "❌ vercel.json missing - creating now..."
    cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "build" }
    }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "/frontend/$1" }
  ]
}
EOF
    echo "✅ vercel.json created"
fi

if [ -f "render.yaml" ]; then
    echo "✅ render.yaml found"
else
    echo "❌ render.yaml missing - creating now..."
    cat > render.yaml << 'EOF'
services:
  - type: web
    name: fullstack-backend
    env: python
    plan: free
    region: oregon
    root: backend
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT
    autoDeploy: true
EOF
    echo "✅ render.yaml created"
fi

if [ -f "backend/Procfile" ]; then
    echo "✅ backend/Procfile found"
else
    echo "❌ backend/Procfile missing - creating now..."
    echo "web: gunicorn -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:\$PORT" > backend/Procfile
    echo "✅ backend/Procfile created"
fi

# Check .gitignore
echo -e "\n🔒 Checking security configuration..."

if [ -f ".gitignore" ]; then
    echo "✅ .gitignore found"
    if grep -q "\.env" .gitignore; then
        echo "✅ .env files are ignored"
    else
        echo "⚠️  Adding .env to .gitignore"
        echo -e "\n# Environment files\n.env\nbackend/.env\nfrontend/.env" >> .gitignore
    fi
else
    echo "❌ .gitignore missing - creating now..."
    cat > .gitignore << 'EOF'
# Dependencies
node_modules/
backend/__pycache__/
backend/.venv/

# Environment files
.env
backend/.env
frontend/.env

# Build outputs
frontend/build/
backend/uploads/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db
EOF
    echo "✅ .gitignore created"
fi

echo -e "\n🔧 Deployment URLs to use:"
echo "Frontend (Vercel): https://your-app.vercel.app"
echo "Backend (Render):  https://your-backend.onrender.com"

echo -e "\n🌍 Environment Variables Needed:"
echo ""
echo "For Vercel (Frontend):"
echo "  REACT_APP_BACKEND_URL=https://your-backend.onrender.com"
echo ""
echo "For Render (Backend):"
echo "  JWT_SECRET_KEY=your-super-secret-key"
echo "  CORS_ORIGINS=https://your-app.vercel.app"
echo "  MONGO_URL=mongodb+srv://... (optional)"

echo -e "\n✅ Project is ready for deployment!"
echo "Next steps:"
echo "1. Push code to GitHub"
echo "2. Create Vercel project from GitHub repo"
echo "3. Create Render web service from GitHub repo"
echo "4. Set environment variables in both platforms"
echo "5. Test the deployed application"

echo -e "\nSee DEPLOYMENT_GUIDE.md for detailed instructions."