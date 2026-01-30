# AI Travel Planner - Docker Build Script for Windows
# ===================================================

Write-Host "🚀 Starting Docker build for AI Travel Planner..." -ForegroundColor Green

# Function to retry Docker build
function Retry-Build {
    param(
        [int]$MaxAttempts = 3
    )
    
    $attempt = 1
    
    while ($attempt -le $MaxAttempts) {
        Write-Host "📦 Build attempt $attempt of $MaxAttempts..." -ForegroundColor Yellow
        
        try {
            docker build -t ai-travel-planner:latest .
            Write-Host "✅ Build successful on attempt $attempt!" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "❌ Build failed on attempt $attempt" -ForegroundColor Red
            if ($attempt -lt $MaxAttempts) {
                Write-Host "🔄 Retrying in 10 seconds..." -ForegroundColor Yellow
                Start-Sleep -Seconds 10
            }
            $attempt++
        }
    }
    
    Write-Host "💥 All build attempts failed!" -ForegroundColor Red
    return $false
}

# Clean up Docker system
Write-Host "🧹 Cleaning up Docker system..." -ForegroundColor Cyan
docker system prune -f

# Check Docker daemon status
Write-Host "🔍 Checking Docker daemon status..." -ForegroundColor Cyan
try {
    docker info | Out-Null
    Write-Host "✅ Docker daemon is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker daemon is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Set environment variables for better build performance
$env:DOCKER_BUILDKIT = "1"
$env:BUILDKIT_PROGRESS = "plain"

# Try building with retry logic
if (Retry-Build) {
    Write-Host "🎉 Docker build completed successfully!" -ForegroundColor Green
    Write-Host "📋 To run the container:" -ForegroundColor Cyan
    Write-Host "   docker run -p 8000:8000 ai-travel-planner:latest" -ForegroundColor White
}
else {
    Write-Host "💥 Docker build failed after all attempts." -ForegroundColor Red
    Write-Host "🔧 Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "   1. Restart Docker Desktop" -ForegroundColor White
    Write-Host "   2. Increase Docker memory allocation (8GB+ recommended)" -ForegroundColor White
    Write-Host "   3. Check available disk space" -ForegroundColor White
    Write-Host "   4. Try building with: docker build --no-cache -t ai-travel-planner:latest ." -ForegroundColor White
    exit 1
}
