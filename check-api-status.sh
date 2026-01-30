#!/bin/bash
# Check API Status on ai2.trekio.net
# ==================================

echo "🔍 Checking AI Travel Planner API Status on ai2.trekio.net"
echo "=========================================================="

# Check if the application is running
echo "1. Checking if API is running..."
if curl -f http://ai2.trekio.net:8000/health > /dev/null 2>&1; then
    echo "✅ API is running on port 8000"
    echo "📱 API URL: http://ai2.trekio.net:8000"
else
    echo "❌ API is not running on port 8000"
    echo "🔧 You need to start the API service"
fi

# Check if the application files exist
echo -e "\n2. Checking application files..."
if [ -f "/home/trekio/public_html/create-plan-ai/app.py" ]; then
    echo "✅ Application files found"
else
    echo "❌ Application files not found"
    echo "🔧 You need to deploy the application"
fi

# Check if database exists
echo -e "\n3. Checking database..."
if [ -f "/home/trekio/public_html/create-plan-ai/poi.db" ]; then
    echo "✅ Database file found"
else
    echo "❌ Database file not found"
    echo "🔧 You need to upload the database file"
fi

# Check if Python dependencies are installed
echo -e "\n4. Checking Python environment..."
if [ -d "/home/trekio/public_html/create-plan-ai/venv" ]; then
    echo "✅ Virtual environment found"
else
    echo "❌ Virtual environment not found"
    echo "🔧 You need to set up Python environment"
fi

echo -e "\n📋 Summary:"
echo "==========="
echo "If all checks pass, your API should be working!"
echo "If any checks fail, follow the setup instructions."
