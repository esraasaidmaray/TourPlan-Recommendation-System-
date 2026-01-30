#!/bin/bash
# AI Travel Planner - Production Deployment Script for Company Server
# ===================================================================

set -e  # Exit on any error

echo "🚀 Starting AI Travel Planner Production Deployment..."
echo "🏢 Company Server Subnet Configuration"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPANY_DOMAIN="travel-planner.yourcompany.com"
INTERNAL_DOMAIN="internal-travel-planner"
COMPANY_SUBNET="192.168.1.0/24"

echo -e "${BLUE}📋 Deployment Configuration:${NC}"
echo "   Company Domain: $COMPANY_DOMAIN"
echo "   Internal Domain: $INTERNAL_DOMAIN"
echo "   Company Subnet: $COMPANY_SUBNET"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if database exists
if [ ! -f "poi.db" ]; then
    echo -e "${RED}❌ Database file 'poi.db' not found. Please ensure the database is present.${NC}"
    exit 1
fi

# Check if SSL certificates exist
if [ ! -f "ssl/travel-planner.crt" ] || [ ! -f "ssl/travel-planner.key" ]; then
    echo -e "${YELLOW}⚠️  SSL certificates not found. Creating self-signed certificates for testing...${NC}"
    mkdir -p ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/travel-planner.key \
        -out ssl/travel-planner.crt \
        -subj "/C=US/ST=State/L=City/O=Company/CN=$COMPANY_DOMAIN"
    echo -e "${GREEN}✅ Self-signed SSL certificates created${NC}"
fi

# Create production environment file
echo -e "${YELLOW}📝 Creating production environment configuration...${NC}"
if [ ! -f ".env" ]; then
    cp env.production .env
    echo -e "${YELLOW}⚠️  Please update .env file with your production settings:${NC}"
    echo "   - SECRET_KEY: Change to a secure random string"
    echo "   - API_KEY: Set your mobile app API key"
    echo "   - ALLOWED_ORIGINS: Add your mobile app domains"
    echo "   - COMPANY_SUBNET: Update with your actual subnet"
    echo ""
    read -p "Press Enter to continue after updating .env file..."
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p logs/nginx
mkdir -p monitoring
mkdir -p ssl

# Create monitoring configuration
echo -e "${YELLOW}📊 Setting up monitoring configuration...${NC}"
cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'travel-planner-api'
    static_configs:
      - targets: ['travel-planner-api-1:8000', 'travel-planner-api-2:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    metrics_path: '/nginx_status'
    scrape_interval: 30s
EOF

# Build and start services
echo -e "${YELLOW}🔨 Building Docker images...${NC}"
docker-compose -f docker-compose.production.yml build

echo -e "${YELLOW}🚀 Starting production services...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 15

# Health check
echo -e "${YELLOW}🏥 Performing health checks...${NC}"

# Check internal API
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Internal API is healthy${NC}"
else
    echo -e "${RED}❌ Internal API health check failed${NC}"
fi

# Check external API
if curl -f -k https://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ External API is healthy${NC}"
else
    echo -e "${RED}❌ External API health check failed${NC}"
fi

# Check monitoring
if curl -f http://localhost:9090 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus monitoring is running${NC}"
else
    echo -e "${RED}❌ Prometheus monitoring failed${NC}"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana dashboards are running${NC}"
else
    echo -e "${RED}❌ Grafana dashboards failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Production deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Service URLs:${NC}"
echo "   🌐 External API (HTTPS): https://$COMPANY_DOMAIN"
echo "   🔒 Internal API (HTTP):  http://$INTERNAL_DOMAIN:8080"
echo "   📱 Mobile API:           https://$COMPANY_DOMAIN/mobile/"
echo "   📚 API Documentation:    https://$COMPANY_DOMAIN/docs (Company subnet only)"
echo "   🏥 Health Check:         https://$COMPANY_DOMAIN/health"
echo "   📊 Prometheus:           http://localhost:9090"
echo "   📈 Grafana:              http://localhost:3000 (admin/admin123)"
echo ""
echo -e "${BLUE}📱 Mobile App Integration:${NC}"
echo "   Base URL: https://$COMPANY_DOMAIN/mobile/"
echo "   API Key: (Set in .env file)"
echo "   CORS: Configured for mobile apps"
echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo "   View logs:           docker-compose -f docker-compose.production.yml logs -f"
echo "   Stop services:       docker-compose -f docker-compose.production.yml down"
echo "   Restart services:    docker-compose -f docker-compose.production.yml restart"
echo "   Update services:     docker-compose -f docker-compose.production.yml pull && docker-compose -f docker-compose.production.yml up -d"
echo "   Scale API instances: docker-compose -f docker-compose.production.yml up -d --scale travel-planner-api-1=3"
echo ""
echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "   1. Update DNS records to point $COMPANY_DOMAIN to this server"
echo "   2. Replace self-signed SSL certificates with production certificates"
echo "   3. Configure firewall rules for company subnet access"
echo "   4. Update mobile app with new API endpoints"
echo "   5. Set up monitoring alerts in Grafana"
echo ""
echo -e "${GREEN}🚀 Your AI Travel Planner is now live and ready for mobile app integration!${NC}"
