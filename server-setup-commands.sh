#!/bin/bash
# AI Travel Planner - Server Setup Commands for ai2.trekio.net
# ============================================================

echo "🚀 Setting up AI Travel Planner on ai2.trekio.net"

# Navigate to project directory
cd /home/trekio/public_html/create-plan-ai

# 1. Check Python version (should be 3.8+)
echo "📋 Checking Python version..."
python3 --version

# 2. Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Check if database file exists
echo "🗄️ Checking database..."
if [ -f "poi.db" ]; then
    echo "✅ Database file found"
    # Test database
    python3 -c "import sqlite3; conn = sqlite3.connect('poi.db'); print(f'POIs in database: {conn.execute(\"SELECT COUNT(*) FROM pois\").fetchone()[0]}'); conn.close()"
else
    echo "❌ Database file not found. Please ensure poi.db is uploaded."
    exit 1
fi

# 5. Test the application
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

# 7. Create systemd service file
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/travel-planner.service > /dev/null << EOF
[Unit]
Description=AI Travel Planner API
After=network.target

[Service]
Type=exec
User=trekio
Group=trekio
WorkingDirectory=/home/trekio/public_html/create-plan-ai
Environment=PATH=/home/trekio/public_html/create-plan-ai/venv/bin
ExecStart=/home/trekio/public_html/create-plan-ai/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 8. Enable and start service
echo "🚀 Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable travel-planner
sudo systemctl start travel-planner

# 9. Check service status
echo "📊 Checking service status..."
sudo systemctl status travel-planner --no-pager

# 10. Test API endpoint
echo "🧪 Testing API endpoint..."
sleep 5
curl -f http://localhost:8000/health || echo "❌ API not responding"

echo "🎉 Setup complete!"
echo "📱 Your API is now running at: http://ai2.trekio.net:8000"
echo "🔍 Health check: http://ai2.trekio.net:8000/health"
echo "📚 API docs: http://ai2.trekio.net:8000/docs"
