#!/bin/bash
# Complete Deployment Script for ai2.trekio.net
# =============================================

echo "🚀 Deploying AI Travel Planner to ai2.trekio.net"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root directory."
    exit 1
fi

# 1. Check Python version
echo "📋 Checking Python version..."
python3 --version

# 2. Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Check database
echo "🗄️ Checking database..."
if [ -f "poi.db" ]; then
    echo "✅ Database file found"
    # Test database
    python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('poi.db')
    count = conn.execute('SELECT COUNT(*) FROM pois').fetchone()[0]
    print(f'✅ Database has {count} POIs')
    conn.close()
except Exception as e:
    print(f'❌ Database error: {e}')
    exit(1)
"
else
    echo "❌ Database file not found. Please ensure poi.db is uploaded."
    exit 1
fi

# 5. Test application imports
echo "🧪 Testing application..."
python3 -c "
import sys
sys.path.append('TourPlan_Recommender')
try:
    from TourPlan_Recommender.itinerary import build_itinerary
    print('✅ Application imports working')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# 6. Create production configuration
echo "⚙️ Creating production configuration..."
cat > .env << EOF
# AI Travel Planner - Production Configuration for ai2.trekio.net
APP_NAME=AI Travel Planner
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database
DATABASE_PATH=poi.db

# Security
SECRET_KEY=$(openssl rand -hex 32)
API_KEY=$(openssl rand -hex 32)

# CORS Configuration
ALLOWED_ORIGINS=https://ai2.trekio.net,https://trekio.net,https://your-mobile-app.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200

# Monitoring
ENABLE_METRICS=True
LOG_FILE_PATH=/home/trekio/public_html/create-plan-ai/app.log
EOF

echo "✅ Configuration created"

# 7. Create startup script
echo "🔧 Creating startup script..."
cat > start-api.sh << 'EOF'
#!/bin/bash
cd /home/trekio/public_html/create-plan-ai
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
EOF

chmod +x start-api.sh

# 8. Test the API
echo "🧪 Testing API startup..."
timeout 10s ./start-api.sh &
API_PID=$!
sleep 5

# Test if API is responding
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is responding"
    kill $API_PID 2>/dev/null
else
    echo "❌ API is not responding"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo "=================================="
echo "📱 Your API is ready at: http://ai2.trekio.net:8000"
echo "🔍 Health check: http://ai2.trekio.net:8000/health"
echo "📚 API docs: http://ai2.trekio.net:8000/docs"
echo ""
echo "🚀 To start the API, run:"
echo "   cd /home/trekio/public_html/create-plan-ai"
echo "   ./start-api.sh"
echo ""
echo "📋 Next steps:"
echo "   1. Set up SSL certificate (see ssl-setup-commands.sh)"
echo "   2. Configure nginx reverse proxy"
echo "   3. Test all endpoints"
echo "   4. Share integration details with backend team"
