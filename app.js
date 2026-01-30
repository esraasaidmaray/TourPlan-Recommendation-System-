# In SSH, navigate to your directory
cd /var/www/vhosts/trekio.net/ai2.trekio.net/httpdocs

# Create a simple Node.js proxy file
cat > app.js << 'EOF'
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const port = process.env.PORT || 3000;

// Proxy all requests to your FastAPI app
app.use('/', createProxyMiddleware({
  target: 'http://127.0.0.1:8001',
  changeOrigin: true
}));

app.listen(port, () => {
  console.log(`Proxy server running on port ${port}`);
});
EOF

// # Install required packages
// npm init -y
// npm install express http-proxy-middleware