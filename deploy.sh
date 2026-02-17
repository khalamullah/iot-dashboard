#!/bin/bash

# IoT Dashboard Deployment Script for AWS EC2/GCP/Azure
# This script automates the deployment process on a fresh Ubuntu server

set -e  # Exit on error

echo "=========================================="
echo "IoT Dashboard Deployment Script"
echo "=========================================="
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv git nginx

# Create application directory
APP_DIR="$HOME/iot-dashboard"
echo "📁 Creating application directory: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# Check if this is a git clone or file upload
if [ -d ".git" ]; then
    echo "📥 Pulling latest changes from git..."
    git pull
else
    echo "⚠️  Not a git repository. Please upload files manually or clone from git."
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOF
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883
MQTT_USER=
MQTT_PASSWORD=
DATABASE_URL=sqlite:///iot_data.db
PORT=8050
DEBUG=False
HOST=0.0.0.0
EOF
    echo "✅ .env file created. Please edit it with your configuration."
fi

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/iot-dashboard.service > /dev/null << EOF
[Unit]
Description=IoT Dashboard Application
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8050 dashboard_multidevice:server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
echo "🚀 Starting IoT Dashboard service..."
sudo systemctl daemon-reload
sudo systemctl enable iot-dashboard
sudo systemctl start iot-dashboard

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/iot-dashboard > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/iot-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Configure firewall
echo "🔒 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8050/tcp
sudo ufw --force enable

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "📊 Dashboard URL: http://$SERVER_IP"
echo "🔧 Service Status: sudo systemctl status iot-dashboard"
echo "📝 View Logs: sudo journalctl -u iot-dashboard -f"
echo "🔄 Restart Service: sudo systemctl restart iot-dashboard"
echo ""
echo "⚙️  Next Steps:"
echo "1. Edit .env file with your MQTT broker details"
echo "2. Restart the service: sudo systemctl restart iot-dashboard"
echo "3. Configure your ESP32 devices to connect"
echo ""
echo "🔐 For HTTPS, install Let's Encrypt:"
echo "   sudo apt install certbot python3-certbot-nginx"
echo "   sudo certbot --nginx -d your-domain.com"
echo ""
echo "=========================================="
