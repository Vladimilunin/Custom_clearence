# Deploy frontend to Vercel
# PowerShell version

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying Frontend to Vercel..." -ForegroundColor Cyan
Write-Host "=" * 40
Write-Host ""

# Check if Vercel CLI is installed
try {
    vercel --version | Out-Null
} catch {
    Write-Host "❌ Vercel CLI not found!" -ForegroundColor Red
    Write-Host "📦 Install it with: npm install -g vercel" -ForegroundColor Yellow
    exit 1
}

# Navigate to frontend directory
Set-Location frontend

# Check if we're logged in
try {
    vercel whoami | Out-Null
} catch {
    Write-Host "🔐 Please login to Vercel..." -ForegroundColor Yellow
    vercel login
}

# Deploy to production
Write-Host "📦 Building and deploying to Vercel..." -ForegroundColor Cyan
vercel --prod

Write-Host ""
Write-Host "=" * 40
Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
Write-Host "=" * 40
Write-Host ""
Write-Host "📝 Don't forget to set environment variables in Vercel dashboard:" -ForegroundColor Yellow
Write-Host "   NEXT_PUBLIC_API_URL - your backend URL (e.g., Cloud Run endpoint)"
Write-Host ""
Write-Host "🌐 Vercel Dashboard: https://vercel.com/dashboard" -ForegroundColor Cyan
