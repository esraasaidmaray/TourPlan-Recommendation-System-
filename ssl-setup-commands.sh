#!/bin/bash
# SSL Certificate Setup for ai2.trekio.net
# ========================================

echo "🔒 Setting up SSL certificate for ai2.trekio.net"

# 1. Install Certbot
echo "📦 Installing Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. Stop nginx temporarily
echo "⏸️ Stopping nginx..."
sudo systemctl stop nginx

# 3. Get SSL certificate
echo "🔐 Getting SSL certificate..."
sudo certbot certonly --standalone -d ai2.trekio.net --non-interactive --agree-tos --email admin@trekio.net

# 4. Copy nginx configuration
echo "⚙️ Configuring nginx..."
sudo cp nginx-config-ai2.trekio.net.conf /etc/nginx/sites-available/ai2.trekio.net
sudo ln -sf /etc/nginx/sites-available/ai2.trekio.net /etc/nginx/sites-enabled/

# 5. Test nginx configuration
echo "🧪 Testing nginx configuration..."
sudo nginx -t

# 6. Start nginx
echo "🚀 Starting nginx..."
sudo systemctl start nginx
sudo systemctl enable nginx

# 7. Set up automatic renewal
echo "🔄 Setting up automatic renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx") | crontab -

echo "✅ SSL setup complete!"
echo "🌐 Your API is now available at: https://ai2.trekio.net"
echo "📱 Mobile API: https://ai2.trekio.net/mobile/"
