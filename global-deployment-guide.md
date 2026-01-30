# 🌐 Global Deployment Guide
## AI Travel Planner - Company Server Integration

### 🏢 Company Server Subnet Configuration

This guide will help you deploy the AI Travel Planner to your company's server subnet with global URL access and mobile app integration.

### 📋 Prerequisites

1. **Server Requirements:**
   - Ubuntu 20.04+ or CentOS 8+
   - Docker & Docker Compose installed
   - Minimum 4GB RAM, 2 CPU cores
   - 20GB free disk space
   - Network access to company subnet

2. **Network Requirements:**
   - Company subnet access (e.g., 192.168.1.0/24)
   - Public IP address for global access
   - Domain name for SSL certificates
   - Firewall rules configured

3. **DNS Configuration:**
   - `travel-planner.yourcompany.com` → Public IP
   - `internal-travel-planner` → Internal IP (company subnet)

### 🚀 Step-by-Step Deployment

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply docker group changes
```

#### Step 2: Clone and Configure

```bash
# Clone your repository
git clone https://github.com/yourcompany/create-plan-ai.git
cd create-plan-ai

# Copy production configuration
cp env.production .env

# Edit configuration
nano .env
```

**Update these values in `.env`:**
```bash
# Security
SECRET_KEY=your-super-secure-random-key-here
API_KEY=your-mobile-app-api-key-here

# Company Configuration
COMPANY_SUBNET=192.168.1.0/24  # Your actual subnet
EXTERNAL_API_URL=https://travel-planner.yourcompany.com
INTERNAL_API_URL=http://internal-travel-planner:8000

# Mobile App Domains
ALLOWED_ORIGINS=https://your-mobile-app.com,https://app.yourcompany.com
```

#### Step 3: SSL Certificate Setup

**Option A: Let's Encrypt (Recommended)**
```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d travel-planner.yourcompany.com

# Copy certificates
sudo cp /etc/letsencrypt/live/travel-planner.yourcompany.com/fullchain.pem ssl/travel-planner.crt
sudo cp /etc/letsencrypt/live/travel-planner.yourcompany.com/privkey.pem ssl/travel-planner.key
sudo chown $USER:$USER ssl/*
```

**Option B: Self-Signed (Testing Only)**
```bash
# Create self-signed certificate
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/travel-planner.key \
    -out ssl/travel-planner.crt \
    -subj "/C=US/ST=State/L=City/O=YourCompany/CN=travel-planner.yourcompany.com"
```

#### Step 4: Deploy Application

```bash
# Make deployment script executable
chmod +x deploy.production.sh

# Run deployment
./deploy.production.sh
```

#### Step 5: Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow internal API (company subnet only)
sudo ufw allow from 192.168.1.0/24 to any port 8080

# Allow monitoring (optional)
sudo ufw allow from 192.168.1.0/24 to any port 9090  # Prometheus
sudo ufw allow from 192.168.1.0/24 to any port 3000  # Grafana

# Enable firewall
sudo ufw enable
```

#### Step 6: DNS Configuration

Update your DNS records:
```
A    travel-planner.yourcompany.com    → YOUR_PUBLIC_IP
A    internal-travel-planner           → YOUR_INTERNAL_IP
```

### 🌍 Global URL Configuration

#### Production URLs:
- **External API**: `https://travel-planner.yourcompany.com`
- **Mobile API**: `https://travel-planner.yourcompany.com/mobile/`
- **Internal API**: `http://internal-travel-planner:8080` (company subnet only)
- **Documentation**: `https://travel-planner.yourcompany.com/docs` (company subnet only)

#### Testing URLs:
- **Test API**: `https://travel-planner-test.yourcompany.com`
- **Staging API**: `https://travel-planner-staging.yourcompany.com`

### 📱 Mobile App Integration

#### API Configuration:
```javascript
// Production
const API_BASE_URL = 'https://travel-planner.yourcompany.com/mobile';
const API_KEY = 'your-mobile-app-api-key-here';

// Testing
const API_BASE_URL_TEST = 'https://travel-planner-test.yourcompany.com/mobile';
```

#### CORS Configuration:
The API is configured to accept requests from:
- Your mobile app domains
- Company internal domains
- Development/testing domains

### 🔒 Security Configuration

#### 1. API Key Management
```bash
# Generate secure API key
openssl rand -hex 32
```

#### 2. Rate Limiting
- **External API**: 20 requests/second per IP
- **Internal API**: 100 requests/second per IP
- **Health Check**: 5 requests/second per IP

#### 3. Network Security
- Company subnet access only for internal endpoints
- SSL/TLS encryption for all external communication
- Security headers configured in Nginx

### 📊 Monitoring Setup

#### Prometheus Metrics:
- **URL**: `http://your-server:9090`
- **Metrics**: API response times, error rates, request counts

#### Grafana Dashboards:
- **URL**: `http://your-server:3000`
- **Login**: admin/admin123
- **Dashboards**: Pre-configured for API monitoring

#### Health Monitoring:
```bash
# Check API health
curl https://travel-planner.yourcompany.com/health

# Check internal API
curl http://internal-travel-planner:8080/health
```

### 🔧 Maintenance Commands

#### View Logs:
```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f travel-planner-api-1
```

#### Restart Services:
```bash
# Restart all
docker-compose -f docker-compose.production.yml restart

# Restart specific service
docker-compose -f docker-compose.production.yml restart travel-planner-api-1
```

#### Scale Services:
```bash
# Scale API instances
docker-compose -f docker-compose.production.yml up -d --scale travel-planner-api-1=3
```

#### Update Application:
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

### 🧪 Testing Your Deployment

#### 1. Health Check:
```bash
curl -k https://travel-planner.yourcompany.com/health
```

#### 2. API Test:
```bash
curl -k -X POST https://travel-planner.yourcompany.com/mobile/itinerary \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-mobile-app-api-key-here" \
  -d '{
    "city": "Cairo",
    "country": "Egypt",
    "theme": "cultural",
    "plan_size": 3
  }'
```

#### 3. Mobile App Test:
Use the provided mobile app integration examples to test from your mobile application.

### 🆘 Troubleshooting

#### Common Issues:

1. **SSL Certificate Errors:**
   ```bash
   # Check certificate
   openssl x509 -in ssl/travel-planner.crt -text -noout
   
   # Renew Let's Encrypt certificate
   sudo certbot renew
   ```

2. **Database Connection Issues:**
   ```bash
   # Check database file
   ls -la poi.db
   
   # Test database
   sqlite3 poi.db "SELECT COUNT(*) FROM pois;"
   ```

3. **Network Connectivity:**
   ```bash
   # Test internal connectivity
   curl http://internal-travel-planner:8080/health
   
   # Test external connectivity
   curl https://travel-planner.yourcompany.com/health
   ```

4. **Docker Issues:**
   ```bash
   # Check container status
   docker-compose -f docker-compose.production.yml ps
   
   # Check container logs
   docker-compose -f docker-compose.production.yml logs travel-planner-api-1
   ```

### 📞 Support

For deployment support:
- **Technical Issues**: Check logs and monitoring dashboards
- **Network Issues**: Verify firewall and DNS configuration
- **API Issues**: Test endpoints and check API key configuration

### 🎉 Success!

Once deployed, your AI Travel Planner will be:
- ✅ Accessible globally via HTTPS
- ✅ Integrated with your mobile application
- ✅ Monitored and secured
- ✅ Scalable and maintainable
- ✅ Ready for production traffic

**Your global URL**: `https://travel-planner.yourcompany.com`
**Mobile API**: `https://travel-planner.yourcompany.com/mobile/`
