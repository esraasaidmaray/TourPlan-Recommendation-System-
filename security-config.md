# 🔒 Security Configuration Guide
## AI Travel Planner - Production Security Setup

### 🛡️ Security Overview

This guide covers the complete security configuration for your AI Travel Planner deployment, including API authentication, network security, and mobile app integration security.

### 🔑 API Authentication

#### 1. API Key Management

**Generate Secure API Keys:**
```bash
# Generate a secure API key (32 bytes, hex encoded)
openssl rand -hex 32

# Example output: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

**API Key Configuration:**
```bash
# In your .env file
API_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
SECRET_KEY=your-super-secure-secret-key-for-jwt-tokens
```

#### 2. API Key Validation Middleware

The API validates API keys on all mobile endpoints:
```http
X-API-Key: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

**Invalid API Key Response:**
```json
{
  "success": false,
  "error": "UNAUTHORIZED",
  "message": "Invalid or missing API key",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_12345"
}
```

### 🌐 Network Security

#### 1. Firewall Configuration

**UFW (Ubuntu Firewall):**
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (if needed)
sudo ufw allow 22/tcp

# Allow internal API (company subnet only)
sudo ufw allow from 192.168.1.0/24 to any port 8080

# Allow monitoring (company subnet only)
sudo ufw allow from 192.168.1.0/24 to any port 9090  # Prometheus
sudo ufw allow from 192.168.1.0/24 to any port 3000  # Grafana

# Deny all other traffic
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable firewall
sudo ufw enable
```

**iptables Configuration:**
```bash
# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow HTTP and HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow internal API (company subnet only)
iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 8080 -j ACCEPT

# Allow monitoring (company subnet only)
iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 9090 -j ACCEPT
iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 3000 -j ACCEPT

# Deny all other traffic
iptables -A INPUT -j DROP
```

#### 2. SSL/TLS Configuration

**Strong SSL Configuration in Nginx:**
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

**SSL Certificate Renewal (Let's Encrypt):**
```bash
# Set up automatic renewal
sudo crontab -e

# Add this line for daily renewal check
0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

### 🔐 Application Security

#### 1. Input Validation

**API Input Validation:**
- All inputs are validated using Pydantic models
- SQL injection protection through parameterized queries
- XSS protection through input sanitization
- File upload restrictions (if applicable)

**Example Validation:**
```python
class ItineraryRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100, regex=r'^[a-zA-Z\s\-\.]+$')
    country: str = Field(..., min_length=1, max_length=100, regex=r'^[a-zA-Z\s\-\.]+$')
    theme: Optional[str] = Field(None, regex=r'^[a-z]+$')
    plan_size: int = Field(6, ge=1, le=20)
    start_time: str = Field("09:00", regex=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    end_time: str = Field("22:00", regex=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    language: str = Field("en", min_length=2, max_length=5, regex=r'^[a-z]{2,5}$')
```

#### 2. Rate Limiting

**Nginx Rate Limiting:**
```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;
limit_req_zone $binary_remote_addr zone=health:10m rate=5r/s;

# Apply rate limiting
limit_req zone=api burst=50 nodelay;
```

**Application-Level Rate Limiting:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/itinerary")
@limiter.limit("10/minute")
async def generate_itinerary(request: Request, itinerary_request: ItineraryRequest):
    # Implementation
```

#### 3. CORS Configuration

**Secure CORS Setup:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-mobile-app.com",
        "https://app.yourcompany.com",
        "https://yourcompany.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
    expose_headers=["X-Request-ID"],
    max_age=3600
)
```

### 📱 Mobile App Security

#### 1. API Key Storage

**React Native (Secure Storage):**
```javascript
import { MMKV } from 'react-native-mmkv';

const storage = new MMKV({
    id: 'travel-planner-storage',
    encryptionKey: 'your-encryption-key'
});

// Store API key securely
storage.set('api_key', 'your-mobile-app-api-key-here');

// Retrieve API key
const apiKey = storage.getString('api_key');
```

**Flutter (Secure Storage):**
```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const storage = FlutterSecureStorage(
  aOptions: AndroidOptions(
    encryptedSharedPreferences: true,
  ),
  iOptions: IOSOptions(
    accessibility: KeychainAccessibility.first_unlock_this_device,
  ),
);

// Store API key
await storage.write(key: 'api_key', value: 'your-mobile-app-api-key-here');

// Retrieve API key
String? apiKey = await storage.read(key: 'api_key');
```

#### 2. Certificate Pinning

**React Native Certificate Pinning:**
```javascript
import { NetworkingModule } from 'react-native';

// Configure certificate pinning
const config = {
    certificatePinning: {
        'travel-planner.yourcompany.com': {
            sha256: ['AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=']
        }
    }
};
```

**Flutter Certificate Pinning:**
```dart
import 'package:dio/dio.dart';
import 'package:dio_certificate_pinning/dio_certificate_pinning.dart';

final dio = Dio();
dio.interceptors.add(
    CertificatePinningInterceptor(
        allowedSHAFingerprints: [
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='
        ],
    ),
);
```

### 🔍 Security Headers

**Nginx Security Headers:**
```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
add_header X-Request-ID $request_id always;
```

### 📊 Security Monitoring

#### 1. Log Analysis

**Security Event Logging:**
```python
import logging
from datetime import datetime

# Configure security logging
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Log security events
def log_security_event(event_type, details, request_id):
    security_logger.info(f"SECURITY_EVENT: {event_type} | {details} | RequestID: {request_id}")

# Usage
log_security_event("INVALID_API_KEY", f"IP: {client_ip}", request_id)
log_security_event("RATE_LIMIT_EXCEEDED", f"IP: {client_ip}", request_id)
log_security_event("SUSPICIOUS_REQUEST", f"User-Agent: {user_agent}", request_id)
```

#### 2. Intrusion Detection

**Fail2ban Configuration:**
```bash
# Install fail2ban
sudo apt install fail2ban

# Configure fail2ban
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
```

### 🚨 Security Incident Response

#### 1. Incident Detection

**Automated Alerts:**
```bash
# Set up log monitoring
sudo apt install logwatch

# Configure logwatch
sudo nano /etc/logwatch/conf/logwatch.conf
```

#### 2. Response Procedures

**Security Incident Checklist:**
1. **Immediate Response:**
   - Block suspicious IP addresses
   - Rotate API keys if compromised
   - Check system logs for indicators of compromise

2. **Investigation:**
   - Analyze attack vectors
   - Review access logs
   - Check for data exfiltration

3. **Recovery:**
   - Patch vulnerabilities
   - Update security configurations
   - Notify stakeholders

### 🔧 Security Maintenance

#### 1. Regular Updates

**System Updates:**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

#### 2. Security Audits

**Regular Security Checks:**
```bash
# Check for open ports
sudo netstat -tulpn

# Check SSL certificate validity
openssl x509 -in ssl/travel-planner.crt -text -noout

# Check file permissions
find /app -type f -perm /o+w
```

#### 3. Backup Security

**Secure Backup Configuration:**
```bash
# Encrypt backups
tar -czf - /app | gpg --symmetric --cipher-algo AES256 --output backup-$(date +%Y%m%d).tar.gz.gpg

# Store backups securely
rsync -avz --delete /backups/ user@backup-server:/secure-backups/
```

### ✅ Security Checklist

- [ ] API keys are securely generated and stored
- [ ] SSL/TLS certificates are valid and properly configured
- [ ] Firewall rules are properly configured
- [ ] Rate limiting is enabled and configured
- [ ] CORS is properly configured for mobile apps
- [ ] Security headers are implemented
- [ ] Input validation is comprehensive
- [ ] Logging and monitoring are configured
- [ ] Backup and recovery procedures are in place
- [ ] Incident response procedures are documented
- [ ] Regular security updates are scheduled
- [ ] Security audits are performed regularly

### 🆘 Security Support

For security-related issues:
- **Emergency**: Contact your security team immediately
- **Non-emergency**: Create a security ticket in your system
- **Documentation**: Keep security logs and incident reports

**Remember**: Security is an ongoing process, not a one-time setup. Regular reviews and updates are essential for maintaining a secure system.
