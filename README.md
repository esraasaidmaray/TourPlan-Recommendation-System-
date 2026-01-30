# 🌍 AI Travel Planner - Production Ready

An intelligent travel planning API that generates **personalized, full-day tour plans** based on available tourist places and user preferences.

## ✨ Features

### 🎯 Theme-Based Planning
Generate different itineraries based on 6 distinct travel themes:
- **🏛️ Cultural** - Museums, heritage sites, historic landmarks, architecture
- **🎉 Friends** - Fun activities, social experiences, group adventures  
- **💕 Couples** - Romantic spots, relaxing venues, sunset locations
- **🍽️ Foodies** - Food farms, markets, tasting tours, local restaurants
- **🏔️ Adventure** - Hiking trails, outdoor activities, natural exploration
- **👨‍👩‍👧‍👦 Family** - Family-friendly activities, restaurants, natural exploration

### 🤖 Smart Algorithm
- **Relevance Scoring** - Matches places to themes using keyword analysis
- **Time Optimization** - Assigns activities based on optimal time periods
- **Diversity Selection** - Ensures variety in activity types
- **Hotel Integration** - Always includes exactly one hotel per itinerary

### 📱 Production-Ready API
- **REST API** with FastAPI framework
- **Docker Containerization** for easy deployment
- **Health Monitoring** endpoints
- **Input Validation** with Pydantic
- **Error Handling** and comprehensive logging
- **Security Headers** and CORS support

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Deploy with one command
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Docker
```bash
# Build and run
docker-compose up -d
```

### Option 3: Direct Python
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

### Get Available Themes
```http
GET /themes
```

### Generate Itinerary
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

### Quick Itinerary
```http
GET /itinerary/quick?city=Cairo&country=Egypt&theme=cultural&plan_size=6
```

## 📊 Database

- **5,531 POIs** across multiple countries
- **16,593 text entries** in multiple languages
- **Real-time recommendations** with SQLite
- **Theme classification** for all locations

## 🔧 Configuration

Create `.env` file:
```bash
SECRET_KEY=your-super-secret-key-here
API_KEY=your-api-key-for-mobile-app
ALLOWED_ORIGINS=https://your-mobile-app.com
DEBUG=False
LOG_LEVEL=INFO
```

## 📱 Mobile App Integration

The API is designed for mobile app integration with:
- JSON request/response format
- CORS configuration for cross-origin requests
- Comprehensive error handling
- Health check endpoints for monitoring

## 🐳 Production Deployment

### Docker Services
- **travel-planner-api** - Main FastAPI application
- **nginx** - Reverse proxy with security headers
- **Health checks** - Automatic monitoring

### Security Features
- Rate limiting with Nginx
- Security headers (XSS, CSRF protection)
- Input validation and sanitization
- Non-root Docker user
- CORS configuration

## 📈 Performance

- **FastAPI** async support
- **Multiple workers** for scaling
- **Nginx reverse proxy** for load balancing
- **Efficient SQLite** queries
- **Docker containerization** for consistency

## 🔍 Monitoring

- Health check endpoint: `/health`
- Application logs: `app.log`
- Docker logs: `docker-compose logs -f`
- Interactive API docs: `/docs`

## 📚 Documentation

- **API Documentation**: `http://localhost:8000/docs`
- **Deployment Guide**: `README_DEPLOYMENT.md`
- **Deployment Summary**: `DEPLOYMENT_SUMMARY.md`

## 🛠️ Development

### Project Structure
```
├── app.py                    # Main FastAPI application
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-service setup
├── nginx.conf               # Reverse proxy config
├── deploy.sh                # Automated deployment
├── TourPlan_Recommender/    # Core recommendation engine
│   ├── itinerary.py         # Main algorithm
│   ├── Models.py            # Scoring logic
│   └── ...                  # Other modules
└── poi.db                   # SQLite database
```

### Testing
```bash
# Test core functionality
python -c "from TourPlan_Recommender.itinerary import build_itinerary; print('OK')"

# Test API endpoints
curl http://localhost:8000/health
```

## 🚨 Troubleshooting

### Common Issues
1. **Database not found**: Ensure `poi.db` exists in project root
2. **Port conflicts**: Check if port 8000 is available
3. **Import errors**: Verify Python path includes TourPlan_Recommender
4. **Docker issues**: Ensure Docker is running and accessible

### Logs
```bash
# View application logs
tail -f app.log

# View Docker logs
docker-compose logs -f

# Check container status
docker ps
```

## 📞 Support

- **API Documentation**: `http://your-server:8000/docs`
- **Health Check**: `http://your-server:8000/health`
- **Interactive Docs**: `http://your-server:8000/redoc`

## ✅ Production Checklist

- [x] FastAPI web server with REST endpoints
- [x] Docker containerization and orchestration
- [x] Nginx reverse proxy with security
- [x] Health check and monitoring endpoints
- [x] Input validation and error handling
- [x] CORS configuration for mobile apps
- [x] Rate limiting and security headers
- [x] Comprehensive logging system
- [x] Automated deployment scripts
- [x] Configuration management
- [x] API documentation
- [x] Mobile app integration ready

---

## 🎉 Ready for Production!

The AI Travel Planner is **100% production-ready** for:
- ✅ Company server deployment
- ✅ Mobile app integration
- ✅ Production traffic handling
- ✅ Monitoring and maintenance
- ✅ Scaling and updates

**Deploy with confidence! 🚀**