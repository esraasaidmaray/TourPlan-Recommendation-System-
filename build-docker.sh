#!/bin/bash

# AI Travel Planner - Docker Build Script with Retry Logic
# ========================================================

set -e

echo "🚀 Starting Docker build for AI Travel Planner..."

# Function to retry Docker build
retry_build() {
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "📦 Build attempt $attempt of $max_attempts..."
        
        if docker build -t ai-travel-planner:latest .; then
            echo "✅ Build successful on attempt $attempt!"
            return 0
        else
            echo "❌ Build failed on attempt $attempt"
            if [ $attempt -lt $max_attempts ]; then
                echo "🔄 Retrying in 10 seconds..."
                sleep 10
            fi
            ((attempt++))
        fi
    done
    
    echo "💥 All build attempts failed!"
    return 1
}

# Clean up Docker system
echo "🧹 Cleaning up Docker system..."
docker system prune -f

# Check Docker daemon status
echo "🔍 Checking Docker daemon status..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

# Increase Docker memory limit (if possible)
echo "⚙️  Setting Docker build options..."
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

# Try building with retry logic
if retry_build; then
    echo "🎉 Docker build completed successfully!"
    echo "📋 To run the container:"
    echo "   docker run -p 8000:8000 ai-travel-planner:latest"
else
    echo "💥 Docker build failed after all attempts."
    echo "🔧 Troubleshooting tips:"
    echo "   1. Restart Docker Desktop"
    echo "   2. Increase Docker memory allocation (8GB+ recommended)"
    echo "   3. Check available disk space"
    echo "   4. Try building with: docker build --no-cache -t ai-travel-planner:latest ."
    exit 1
fi
