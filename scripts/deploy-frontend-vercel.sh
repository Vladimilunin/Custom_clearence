#!/bin/bash
# Deploy frontend to Vercel

set -e

echo "🚀 Deploying Frontend to Vercel..."
echo "===================================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found!"
    echo "📦 Install it with: npm install -g vercel"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if we're logged in
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please login to Vercel..."
    vercel login
fi

# Deploy to production
echo "📦 Building and deploying to Vercel..."
vercel --prod

echo ""
echo "===================================="
echo "✅ Frontend deployed successfully!"
echo "===================================="
echo ""
echo "📝 Don't forget to set environment variables in Vercel dashboard:"
echo "   NEXT_PUBLIC_API_URL - your backend URL (e.g., Cloud Run endpoint)"
echo ""
echo "🌐 Vercel Dashboard: https://vercel.com/dashboard"
