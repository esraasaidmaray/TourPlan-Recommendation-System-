# 🚀 AI Travel Planner - Production Deployment Guide

## 📋 Overview

This guide will help you deploy the AI Travel Planner to a company server and integrate it with a mobile application.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │───▶│   Nginx Proxy   │───▶│  FastAPI Server │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                               ┌─────────────────┐
                                               │  SQLite Database│
                                               │   (poi.db)      │
                                               └─────────────────┘
```

## 📦 Components

### Core Files
- `app.py` - FastAPI web server with REST endpoints
- `TourPlan_Recommender/itinerary.py` - Core recommendation engine
- `poi.db` - SQLite database with POI data
- `requirements.txt` - Python dependencies

### Deployment Files
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-service orchestration
- `nginx.conf` - Reverse proxy configuration
- `deploy.sh` - Automated deployment script
- `config.py` - Configuration management

## 🚀 Quick Deployment

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone/upload the project to your server
# 2. Navigate to project directory
cd /path/to/Create-Plan-AI

# 3. Make deployment script executable
chmod +x deploy.sh

# 4. Run deployment
./deploy.sh
```

### Option 2: Manual Docker

```bash
# Build the image
docker build -t travel-planner-api .

# Run the container
docker run -d \
  --name travel-planner-api \
  -p 8000:8000 \
  -v $(pwd)/poi.db:/app/poi.db:ro \
  travel-planner-api
```

### Option 3: Direct Python (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# Application Settings
APP_NAME=AI Travel Planner
DEBUG=False
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-key-here
API_KEY=your-api-key-for-mobile-app

# Database
DATABASE_PATH=poi.db

# CORS (Configure for your mobile app domain)
ALLOWED_ORIGINS=https://your-mobile-app.com,https://your-domain.com
```

## 📱 Mobile App Integration

### API Endpoints

#### 1. Health Check
```http
GET /health
```

#### 2. Get Available Themes
```http
GET /themes
```

#### 3. Generate Itinerary (POST)
```http
POST /itinerary
Content-Type: application/json

{
  "city": "Cairo",
  "country": "Egypt",
  "theme": "cultural",
  "plan_size": 6,
  "start_time": "09:00",
  "end_time": "22:00",
  "language": "en"
}
```

#### 4. Quick Itinerary (GET)
```http
GET /itinerary/quick?city=Cairo&country=Egypt&theme=cultural&plan_size=6
```

### Response Format

```json
{
  "success": true,
  "message": "Generated 6 activities for Cairo",
  "data": {
    "slots": [
      {
        "start": "09:00",
        "end": "11:36",
        "name": "New Royal Grand Hotel Cairo",
        "category": "hotel",
        "score": 1.25
      },
      {
        "start": "11:36",
        "end": "14:12",
        "name": "Abdeen Palace Museum",
        "category": "tourist place",
        "score": 1.25
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "12345"
}
```

## 🔒 Security Considerations

### Production Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_ORIGINS` for your domains
- [ ] Use HTTPS in production
- [ ] Set up API key authentication
- [ ] Configure firewall rules
- [ ] Set up SSL certificates
- [ ] Enable rate limiting

### API Authentication (Optional)

Add API key validation to `app.py`:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Add to endpoints:
@app.post("/itinerary")
async def generate_itinerary(request: ItineraryRequest, api_key: str = Depends(verify_api_key)):
    # ... existing code
```

## 📊 Monitoring & Logging

### Health Monitoring

The API provides a health check endpoint at `/health` that returns:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "database_status": "connected (5531 POIs)"
}
```

### Log Files

- Application logs: `app.log`
- Docker logs: `docker-compose logs -f`
- Nginx logs: Available in nginx container

### Metrics (Optional)

Add Prometheus metrics:

```python
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Not Found
```bash
# Check if poi.db exists
ls -la poi.db

# If missing, ensure you're in the correct directory
pwd
```

#### 2. Port Already in Use
```bash
# Check what's using port 8000
netstat -tulpn | grep :8000

# Kill the process or change port in docker-compose.yml
```

#### 3. Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Ensure TourPlan_Recommender is accessible
python -c "from TourPlan_Recommender.itinerary import build_itinerary; print('OK')"
```

#### 4. Docker Issues
```bash
# Check Docker is running
docker --version

# Check container status
docker ps -a

# View container logs
docker logs travel-planner-api
```

## 📈 Performance Optimization

### Production Settings

1. **Increase Workers**: Set `WORKERS=8` in `.env`
2. **Enable Gunicorn**: Use `gunicorn` instead of `uvicorn` for production
3. **Database Optimization**: Consider PostgreSQL for high traffic
4. **Caching**: Add Redis for caching frequent requests
5. **Load Balancing**: Use multiple API instances behind nginx

### Scaling

```yaml
# docker-compose.yml - Scale API instances
services:
  travel-planner-api:
    # ... existing config
    deploy:
      replicas: 3
```

## 🔄 Updates & Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Database Updates

```bash
# Backup database
cp poi.db poi.db.backup

# Update database (if needed)
python TourPlan_Recommender/ingest.py
```

## 📞 Support

### API Documentation

- Interactive docs: `http://your-server:8000/docs`
- ReDoc: `http://your-server:8000/redoc`

### Testing

```bash
# Run API tests
python test_api.py

# Test specific endpoint
curl -X POST "http://localhost:8000/itinerary" \
  -H "Content-Type: application/json" \
  -d '{"city":"Cairo","country":"Egypt","theme":"cultural","plan_size":4}'
```

---

## ✅ Production Readiness Checklist

- [x] FastAPI web server with REST endpoints
- [x] Docker containerization
- [x] Nginx reverse proxy
- [x] Health check endpoints
- [x] Error handling and logging
- [x] Input validation
- [x] CORS configuration
- [x] Rate limiting
- [x] Security headers
- [x] Automated deployment script
- [x] Configuration management
- [x] API documentation
- [x] Mobile app integration examples

**The project is now ready for production deployment! 🎉**
