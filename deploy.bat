@echo off
echo 🚀 Deploying Markaz Finance Assistant to Streamlit Cloud...

REM Check if git is initialized
if not exist ".git" (
    echo ❌ Git repository not found. Please initialize git first:
    echo    git init
    echo    git add .
    echo    git commit -m "Initial commit"
    pause
    exit /b 1
)

REM Check if remote origin is set
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo ❌ Git remote origin not set. Please add your GitHub repository:
    echo    git remote add origin ^<your-github-repo-url^>
    pause
    exit /b 1
)

REM Push to GitHub
echo 📤 Pushing code to GitHub...
git add .
git commit -m "Prepare for deployment - %date% %time%"
git push origin main

echo ✅ Code pushed to GitHub successfully!
echo.
echo 🌐 Next steps:
echo 1. Go to https://share.streamlit.io
echo 2. Sign in with GitHub
echo 3. Click 'New app'
echo 4. Select your repository
echo 5. Set path to: knowledge/docling/5-chat.py
echo 6. Add your environment variables in the secrets section
echo 7. Click 'Deploy!'
echo.
echo 🔑 Required environment variables:
echo    - AZURE_OPENAI_API_KEY
echo    - AZURE_OPENAI_ENDPOINT
echo    - AZURE_OPENAI_DEPLOYMENT_NAME
echo    - AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
echo    - ACCESS_PASSWORD (for security)
echo.
echo 🎉 Your app will be live at: https://your-app-name.streamlit.app
pause
