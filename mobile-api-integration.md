# 📱 Mobile App Integration Guide
## AI Travel Planner API

### 🌐 Global API Endpoints

**Production URL:** `https://travel-planner.yourcompany.com/mobile/`
**Testing URL:** `https://travel-planner-test.yourcompany.com/mobile/`

### 🔑 Authentication

All mobile app requests must include the API key in the header:
```http
X-API-Key: your-mobile-app-api-key-here
```

### 📋 Available Endpoints

#### 1. Health Check
```http
GET /mobile/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "database_status": "connected (5531 POIs)"
}
```

#### 2. Get Available Themes
```http
GET /mobile/themes
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
POST /mobile/itinerary
Content-Type: application/json
X-API-Key: your-mobile-app-api-key-here

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

**Response:**
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
        "score": 1.25,
        "description": "Luxury hotel in downtown Cairo",
        "location": {
          "latitude": 30.0444,
          "longitude": 31.2357
        },
        "rating": 4.5,
        "price_range": "$$$"
      }
    ],
    "total_duration": "13 hours",
    "theme": "cultural",
    "city": "Cairo",
    "country": "Egypt"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_12345"
}
```

#### 4. Quick Itinerary (GET)
```http
GET /mobile/itinerary/quick?city=Cairo&country=Egypt&theme=cultural&plan_size=6
X-API-Key: your-mobile-app-api-key-here
```

### 📱 Mobile App Implementation Examples

#### React Native (JavaScript)
```javascript
const API_BASE_URL = 'https://travel-planner.yourcompany.com/mobile';
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
        plan_size: 6,
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

struct ItineraryRequest: Codable {
    let city: String
    let country: String
    let theme: String
    let plan_size: Int
    let start_time: String
    let end_time: String
    let language: String
}

struct ItineraryResponse: Codable {
    let success: Bool
    let message: String
    let data: ItineraryData
    let timestamp: String
    let request_id: String
}

struct ItineraryData: Codable {
    let slots: [ActivitySlot]
    let total_duration: String
    let theme: String
    let city: String
    let country: String
}

struct ActivitySlot: Codable {
    let start: String
    let end: String
    let name: String
    let category: String
    let score: Double
    let description: String?
    let location: Location?
    let rating: Double?
    let price_range: String?
}

struct Location: Codable {
    let latitude: Double
    let longitude: Double
}

enum APIError: Error {
    case invalidURL
    case requestFailed
}
```

#### Kotlin (Android)
```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.net.HttpURLConnection
import java.net.URL

class TravelPlannerAPI {
    private val baseURL = "https://travel-planner.yourcompany.com/mobile"
    private val apiKey = "your-mobile-app-api-key-here"
    private val json = Json { ignoreUnknownKeys = true }
    
    suspend fun generateItinerary(
        city: String,
        country: String,
        theme: String = "cultural"
    ): ItineraryResponse = withContext(Dispatchers.IO) {
        val url = URL("$baseURL/itinerary")
        val connection = url.openConnection() as HttpURLConnection
        
        try {
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.setRequestProperty("X-API-Key", apiKey)
            connection.doOutput = true
            
            val request = ItineraryRequest(
                city = city,
                country = country,
                theme = theme,
                plan_size = 6,
                start_time = "09:00",
                end_time = "22:00",
                language = "en"
            )
            
            connection.outputStream.use { outputStream ->
                outputStream.write(json.encodeToString(ItineraryRequest.serializer(), request).toByteArray())
            }
            
            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                json.decodeFromString(ItineraryResponse.serializer(), response)
            } else {
                throw Exception("Request failed with code: $responseCode")
            }
        } finally {
            connection.disconnect()
        }
    }
}

@Serializable
data class ItineraryRequest(
    val city: String,
    val country: String,
    val theme: String,
    val plan_size: Int,
    val start_time: String,
    val end_time: String,
    val language: String
)

@Serializable
data class ItineraryResponse(
    val success: Boolean,
    val message: String,
    val data: ItineraryData,
    val timestamp: String,
    val request_id: String
)

@Serializable
data class ItineraryData(
    val slots: List<ActivitySlot>,
    val total_duration: String,
    val theme: String,
    val city: String,
    val country: String
)

@Serializable
data class ActivitySlot(
    val start: String,
    val end: String,
    val name: String,
    val category: String,
    val score: Double,
    val description: String? = null,
    val location: Location? = null,
    val rating: Double? = null,
    val price_range: String? = null
)

@Serializable
data class Location(
    val latitude: Double,
    val longitude: Double
)
```

### 🔒 Security Considerations

1. **API Key Management**: Store API keys securely in your mobile app
2. **HTTPS Only**: All API calls must use HTTPS
3. **Rate Limiting**: API is rate-limited to 20 requests/second per IP
4. **Input Validation**: All inputs are validated on the server side
5. **CORS**: Configured for mobile app domains

### 📊 Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (missing/invalid API key)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error

Error response format:
```json
{
  "success": false,
  "error": "INVALID_THEME",
  "message": "Invalid theme. Available themes: cultural, adventure, foodies, family, couples, friends",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_12345"
}
```

### 🧪 Testing

Use the testing endpoint for development:
```http
GET https://travel-planner-test.yourcompany.com/mobile/health
```

### 📈 Monitoring

Monitor your API usage through:
- **Prometheus**: `http://your-server:9090`
- **Grafana**: `http://your-server:3000`
- **Health Check**: `https://travel-planner.yourcompany.com/mobile/health`

### 🆘 Support

For technical support or questions:
- **Email**: tech-support@yourcompany.com
- **Documentation**: `https://travel-planner.yourcompany.com/docs`
- **Status Page**: `https://status.yourcompany.com`
