# 📱 Backend Team Integration Package - FINAL
## AI Travel Planner API - Ready for Mobile App Integration

### 🌐 **API Endpoints**

**Base URL**: `http://ai2.trekio.net:9000`
**Health Check**: `http://ai2.trekio.net:9000/health`
**API Documentation**: `http://ai2.trekio.net:9000/docs`

### 🔑 **Authentication**

All mobile app requests must include the API key in the header:
```http
X-API-Key: your-mobile-app-api-key-here
```

### 📋 **Available Endpoints**

#### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-15T00:23:22.575227",
  "version": "1.0.0",
  "database_status": "connected (5531 POIs)"
}
```

#### 2. Get Available Themes
```http
GET /themes
```
**Response:**
```json
{
  "success": true,
  "themes": ["cultural", "adventure", "foodies", "family", "couples", "friends"],
  "descriptions": {
    "cultural": "Museums, heritage sites, historic landmarks, architecture",
    "adventure": "Hiking trails, outdoor activities, natural exploration",
    "foodies": "Food farms, markets, tasting tours, local restaurants",
    "family": "Family-friendly activities, restaurants, natural exploration",
    "couples": "Romantic spots, relaxing venues, sunset locations",
    "friends": "Fun activities, social experiences, group adventures"
  }
}
```

#### 3. Generate Itinerary (POST)
```http
POST /itinerary
Content-Type: application/json
X-API-Key: your-mobile-app-api-key-here

{
  "city": "Cairo",
  "country": "Egypt",
  "theme": "cultural",
  "plan_size": 3,
  "start_time": "09:00",
  "end_time": "22:00",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Generated 3 activities for Cairo",
  "data": {
    "slots": [
      {
        "start": "09:00",
        "end": "13:20",
        "name": "New Royal Grand Hotel Cairo",
        "category": "hotel",
        "score": 1.25
      },
      {
        "start": "13:20",
        "end": "17:40",
        "name": "Abdeen Palace Museum",
        "category": "tourist place",
        "score": 1.25
      },
      {
        "start": "17:40",
        "end": "22:00",
        "name": "Al-Azhar Park",
        "category": "tourist place",
        "score": 1.25
      }
    ]
  },
  "timestamp": "2025-09-15T00:23:44.825531",
  "request_id": "1400964"
}
```

#### 4. Quick Itinerary (GET)
```http
GET /itinerary/quick?city=Cairo&country=Egypt&theme=cultural&plan_size=3
X-API-Key: your-mobile-app-api-key-here
```

### 📱 **Mobile App Integration Examples**

#### React Native
```javascript
const API_BASE_URL = 'http://ai2.trekio.net:9000';
const API_KEY = 'your-mobile-app-api-key-here';

const generateItinerary = async (city, country, theme = 'cultural') => {
  try {
    const response = await fetch(`${API_BASE_URL}/itinerary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify({
        city,
        country,
        theme,
        plan_size: 3,
        start_time: '09:00',
        end_time: '22:00',
        language: 'en'
      })
    });

    const data = await response.json();
    
    if (data.success) {
      return data.data;
    } else {
      throw new Error(data.message);
    }
  } catch (error) {
    console.error('Error generating itinerary:', error);
    throw error;
  }
};

// Usage
generateItinerary('Cairo', 'Egypt', 'cultural')
  .then(itinerary => {
    console.log('Generated itinerary:', itinerary);
  })
  .catch(error => {
    console.error('Failed to generate itinerary:', error);
  });
```

#### Flutter
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class TravelPlannerAPI {
  static const String baseURL = 'http://ai2.trekio.net:9000';
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
        'plan_size': 3,
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
    private let baseURL = "http://ai2.trekio.net:9000"
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
            plan_size: 3,
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

### 🔒 **Security Configuration**

- **API Key Required**: All requests must include valid API key
- **HTTPS Ready**: Can be configured with SSL certificates
- **Rate Limiting**: Configured for production use
- **CORS**: Configured for mobile app domains
- **Input Validation**: All inputs validated on server side

### 📊 **Error Handling**

Standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (missing/invalid API key)
- `422`: Validation Error (missing required fields)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error

Error response format:
```json
{
  "success": false,
  "error": "INVALID_THEME",
  "message": "Invalid theme. Available themes: cultural, adventure, foodies, family, couples, friends",
  "timestamp": "2025-09-15T00:23:44.825531",
  "request_id": "1400964"
}
```

### 🧪 **Testing**

#### Test Endpoints
```bash
# Health Check
curl http://ai2.trekio.net:9000/health

# Get Themes
curl http://ai2.trekio.net:9000/themes

# Generate Itinerary
curl -X POST http://ai2.trekio.net:9000/itinerary \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-mobile-app-api-key-here" \
  -d '{"city": "Cairo", "country": "Egypt", "theme": "cultural", "plan_size": 3}'
```

### 📈 **Monitoring**

- **Health Check**: `http://ai2.trekio.net:9000/health`
- **API Documentation**: `http://ai2.trekio.net:9000/docs`
- **Logs**: Available on server at `api.log`

### 🆘 **Support**

- **API Status**: Check health endpoint
- **Documentation**: Available at `/docs` endpoint
- **Logs**: Check server logs for debugging

### 📋 **Implementation Checklist**

- [ ] Update API base URL in mobile app
- [ ] Configure API key authentication
- [ ] Implement error handling
- [ ] Test all endpoints
- [ ] Configure CORS for your mobile app domain
- [ ] Set up monitoring and logging
- [ ] Test with real data
- [ ] Deploy to production

### 🎯 **Available Themes**

1. **Cultural** 🏛️ - Museums, heritage sites, historic landmarks
2. **Adventure** 🏔️ - Hiking trails, outdoor activities, natural exploration
3. **Foodies** 🍽️ - Food farms, markets, tasting tours, restaurants
4. **Family** 👨‍👩‍👧‍👦 - Family-friendly activities, restaurants, parks
5. **Couples** 💕 - Romantic spots, relaxing venues, sunset locations
6. **Friends** 👥 - Fun activities, social experiences, group adventures

### 🚀 **Ready for Production!**

Your AI Travel Planner API is now:
- ✅ **Live and accessible** at `http://ai2.trekio.net:9000`
- ✅ **Fully tested** with all endpoints working
- ✅ **Mobile app ready** with comprehensive examples
- ✅ **Production ready** with error handling and validation
- ✅ **Running in background** - no need to keep terminal open
- ✅ **Scalable** with proper architecture

---

**🎉 Your AI Travel Planner API is ready for mobile app integration!**
