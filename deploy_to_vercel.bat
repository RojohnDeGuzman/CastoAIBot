@echo off
echo ========================================
echo CASI AI Bot - Deployment Script
echo ========================================
echo.

echo Step 1: Checking Git status...
git status

echo.
echo Step 2: Adding all files to Git...
git add .

echo.
echo Step 3: Committing changes...
git commit -m "Update for Vercel deployment"

echo.
echo Step 4: Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo Deployment to GitHub Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Go to https://vercel.com
echo 2. Sign in with GitHub
echo 3. Click "New Project"
echo 4. Import your CastoAIBot repository
echo 5. Set environment variable GROQ_API_KEY
echo 6. Deploy!
echo.
echo Your backend will be available at:
echo https://your-project-name.vercel.app
echo.
pause
