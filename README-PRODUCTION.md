# 🚀 AI Travel Planner - Production Deployment
## Complete Guide for Company Server Integration & Mobile App

### 📋 Overview

This guide provides everything you need to deploy the AI Travel Planner to your company's server subnet with global URL access and mobile app integration.

### 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   Web Browser   │    │  Company Users  │
│                 │    │                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ HTTPS                │ HTTPS                │ HTTP
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx Load Balancer                         │
│              (SSL Termination + Rate Limiting)                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                Docker Container Network                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   API Instance  │  │   API Instance  │  │   Redis Cache   │ │
│  │       #1        │  │       #2        │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Prometheus    │  │     Grafana     │  │   SQLite DB     │ │
│  │   Monitoring    │  │   Dashboards    │  │   (POI Data)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 🌐 Global URLs

| Service | URL | Access |
|---------|-----|--------|
| **Production API** | `https://travel-planner.yourcompany.com` | Public |
| **Mobile API** | `https://travel-planner.yourcompany.com/mobile/` | Mobile Apps |
| **Internal API** | `http://internal-travel-planner:8080` | Company Subnet |
| **API Docs** | `https://travel-planner.yourcompany.com/docs` | Company Subnet |
| **Monitoring** | `http://your-server:3000` | Company Subnet |

### 📱 Mobile App Integration

#### Quick Start
```javascript
// Initialize SDK
const travelPlanner = new TravelPlannerSDK({
    baseURL: 'https://travel-planner.yourcompany.com/mobile',
    apiKey: 'your-mobile-app-api-key-here'
});

// Generate itinerary
const itinerary = await travelPlanner.generateItinerary({
    city: 'Cairo',
    country: 'Egypt',
    theme: 'cultural',
    planSize: 6
});
```

#### Available Themes
- 🏛️ **Cultural** - Museums, heritage sites, historic landmarks
- 🏔️ **Adventure** - Hiking trails, outdoor activities, natural exploration
- 🍽️ **Foodies** - Food farms, markets, tasting tours, restaurants
- 👨‍👩‍👧‍👦 **Family** - Family-friendly activities, restaurants, parks
- 💕 **Couples** - Romantic spots, relaxing venues, sunset locations
- 👥 **Friends** - Fun activities, social experiences, group adventures

### 🚀 Quick Deployment

#### 1. Prerequisites
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Deploy
```bash
# Clone repository
git clone https://github.com/yourcompany/create-plan-ai.git
cd create-plan-ai

# Configure environment
cp env.production .env
nano .env  # Update with your settings

# Deploy
chmod +x deploy.production.sh
./deploy.production.sh
```

#### 3. Configure DNS
```
A    travel-planner.yourcompany.com    → YOUR_PUBLIC_IP
A    internal-travel-planner           → YOUR_INTERNAL_IP
```

### 🔧 Configuration

#### Environment Variables
```bash
# Security
SECRET_KEY=your-super-secure-random-key-here
API_KEY=your-mobile-app-api-key-here

# Company Configuration
COMPANY_SUBNET=192.168.1.0/24
EXTERNAL_API_URL=https://travel-planner.yourcompany.com
INTERNAL_API_URL=http://internal-travel-planner:8000

# Mobile App Domains
ALLOWED_ORIGINS=https://your-mobile-app.com,https://app.yourcompany.com
```

#### SSL Certificates
```bash
# Let's Encrypt (Recommended)
sudo certbot certonly --standalone -d travel-planner.yourcompany.com

# Copy certificates
sudo cp /etc/letsencrypt/live/travel-planner.yourcompany.com/fullchain.pem ssl/travel-planner.crt
sudo cp /etc/letsencrypt/live/travel-planner.yourcompany.com/privkey.pem ssl/travel-planner.key
```

### 🔒 Security Features

- ✅ **API Key Authentication** - Secure mobile app access
- ✅ **SSL/TLS Encryption** - All traffic encrypted
- ✅ **Rate Limiting** - 20 requests/second per IP
- ✅ **CORS Protection** - Configured for mobile apps
- ✅ **Input Validation** - Comprehensive request validation
- ✅ **Security Headers** - XSS, CSRF, and clickjacking protection
- ✅ **Firewall Rules** - Company subnet access control
- ✅ **Monitoring** - Real-time security monitoring

### 📊 Monitoring & Analytics

#### Prometheus Metrics
- API response times
- Error rates
- Request counts
- System resource usage

#### Grafana Dashboards
- Real-time API performance
- Error rate monitoring
- User activity analytics
- System health status

#### Health Checks
```bash
# API Health
curl https://travel-planner.yourcompany.com/health

# Mobile API Health
curl https://travel-planner.yourcompany.com/mobile/health

# Internal API Health
curl http://internal-travel-planner:8080/health
```

### 🧪 Testing

#### Run Test Suite
```bash
# Install Node.js dependencies
npm install

# Run comprehensive tests
node test-api.js
```

#### Test Results
```
🚀 Starting AI Travel Planner API Tests
=====================================
✅ Health Check - PASSED
✅ Mobile API Health Check - PASSED
✅ Get Themes - PASSED
✅ Generate Itinerary (POST) - PASSED
✅ Quick Itinerary (GET) - PASSED
✅ Invalid API Key - PASSED
✅ Missing API Key - PASSED
✅ Invalid Theme - PASSED
✅ Missing Required Fields - PASSED
✅ Rate Limiting - PASSED
✅ Internal API Access - PASSED
✅ SSL Certificate - PASSED
✅ CORS Headers - PASSED
✅ Response Time - PASSED
✅ Error Handling - PASSED

📊 Test Results Summary
======================
✅ Passed: 15
❌ Failed: 0
📈 Success Rate: 100.0%

🎉 All tests passed! Your API is ready for production.
```

### 🔧 Maintenance

#### View Logs
```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f travel-planner-api-1
```

#### Restart Services
```bash
# Restart all
docker-compose -f docker-compose.production.yml restart

# Restart specific service
docker-compose -f docker-compose.production.yml restart travel-planner-api-1
```

#### Scale Services
```bash
# Scale API instances
docker-compose -f docker-compose.production.yml up -d --scale travel-planner-api-1=3
```

#### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

### 📱 Mobile App Examples

#### React Native
```javascript
import { TravelPlannerSDK } from './mobile-app-sdk';

const sdk = new TravelPlannerSDK({
    baseURL: 'https://travel-planner.yourcompany.com/mobile',
    apiKey: 'your-mobile-app-api-key-here'
});

const itinerary = await sdk.generateItinerary({
    city: 'Cairo',
    country: 'Egypt',
    theme: 'cultural'
});
```

#### Flutter
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class TravelPlannerAPI {
    static const String baseURL = 'https://travel-planner.yourcompany.com/mobile';
    static const String apiKey = 'your-mobile-app-api-key-here';
    
    static Future<Map<String, dynamic>> generateItinerary({
        required String city,
        required String country,
        String theme = 'cultural',
    }) async {
        final response = await http.post(
            Uri.parse('$baseURL/itinerary'),
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey,
            },
            body: jsonEncode({
                'city': city,
                'country': country,
                'theme': theme,
                'plan_size': 6,
                'start_time': '09:00',
                'end_time': '22:00',
                'language': 'en',
            }),
        );
        
        return jsonDecode(response.body);
    }
}
```

#### Swift (iOS)
```swift
import Foundation

class TravelPlannerAPI {
    private let baseURL = "https://travel-planner.yourcompany.com/mobile"
    private let apiKey = "your-mobile-app-api-key-here"
    
    func generateItinerary(city: String, country: String, theme: String = "cultural") async throws -> ItineraryResponse {
        guard let url = URL(string: "\(baseURL)/itinerary") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        
        let requestBody = ItineraryRequest(
            city: city,
            country: country,
            theme: theme,
            plan_size: 6,
            start_time: "09:00",
            end_time: "22:00",
            language: "en"
        )
        
        request.httpBody = try JSONEncoder().encode(requestBody)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.requestFailed
        }
        
        return try JSONDecoder().decode(ItineraryResponse.self, from: data)
    }
}
```

### 🆘 Troubleshooting

#### Common Issues

1. **SSL Certificate Errors**
   ```bash
   # Check certificate
   openssl x509 -in ssl/travel-planner.crt -text -noout
   
   # Renew Let's Encrypt certificate
   sudo certbot renew
   ```

2. **Database Connection Issues**
   ```bash
   # Check database file
   ls -la poi.db
   
   # Test database
   sqlite3 poi.db "SELECT COUNT(*) FROM pois;"
   ```

3. **Network Connectivity**
   ```bash
   # Test internal connectivity
   curl http://internal-travel-planner:8080/health
   
   # Test external connectivity
   curl https://travel-planner.yourcompany.com/health
   ```

4. **Docker Issues**
   ```bash
   # Check container status
   docker-compose -f docker-compose.production.yml ps
   
   # Check container logs
   docker-compose -f docker-compose.production.yml logs travel-planner-api-1
   ```

### 📞 Support

- **Technical Issues**: Check logs and monitoring dashboards
- **Network Issues**: Verify firewall and DNS configuration
- **API Issues**: Test endpoints and check API key configuration
- **Mobile Integration**: Use provided SDK and examples

### 🎉 Success!

Once deployed, your AI Travel Planner will be:
- ✅ **Globally Accessible** via HTTPS
- ✅ **Mobile App Ready** with comprehensive SDK
- ✅ **Secure & Monitored** with enterprise-grade security
- ✅ **Scalable & Maintainable** with Docker orchestration
- ✅ **Production Ready** with comprehensive testing

**Your global URL**: `https://travel-planner.yourcompany.com`
**Mobile API**: `https://travel-planner.yourcompany.com/mobile/`

---

**🚀 Ready to deploy? Run `./deploy.production.sh` and your AI Travel Planner will be live!**
