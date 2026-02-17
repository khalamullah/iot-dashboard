# IoT Dashboard - Cloud Deployment Guide

This guide provides step-by-step instructions for deploying your IoT Dashboard to various cloud platforms.

## 📋 Table of Contents

1. [Deployment Options Overview](#deployment-options-overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Option 1: AWS EC2 (Recommended)](#option-1-aws-ec2-recommended)
4. [Option 2: Google Cloud Platform](#option-2-google-cloud-platform)
5. [Option 3: Microsoft Azure](#option-3-microsoft-azure)
6. [Option 4: Heroku (Easiest)](#option-4-heroku-easiest)
7. [Option 5: Railway (Modern & Simple)](#option-5-railway-modern--simple)
8. [MQTT Broker Setup](#mqtt-broker-setup)
9. [Database Configuration](#database-configuration)
10. [Security Best Practices](#security-best-practices)
11. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🎯 Deployment Options Overview

| Platform         | Difficulty      | Cost                      | Best For                         |
| ---------------- | --------------- | ------------------------- | -------------------------------- |
| **Railway**      | ⭐ Easy         | Free tier available       | Quick deployment, beginners      |
| **Heroku**       | ⭐⭐ Easy       | Free tier (limited)       | Simple deployment                |
| **AWS EC2**      | ⭐⭐⭐ Moderate | Pay-as-you-go             | Full control, scalability        |
| **Google Cloud** | ⭐⭐⭐ Moderate | Free tier + pay-as-you-go | Integration with Google services |
| **Azure**        | ⭐⭐⭐ Moderate | Free tier + pay-as-you-go | Enterprise, Microsoft ecosystem  |

---

## ✅ Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] Python application tested locally
- [ ] All dependencies listed in `requirements.txt`
- [ ] MQTT broker accessible (public or cloud-hosted)
- [ ] Database strategy decided (SQLite or PostgreSQL)
- [ ] Environment variables identified
- [ ] Security configurations reviewed

### Required Files

Create these files in your project root:

#### 1. `Procfile` (for Heroku/Railway)

```
web: gunicorn dashboard_multidevice:server
```

#### 2. `runtime.txt` (for Heroku)

```
python-3.11.0
```

#### 3. Update `requirements.txt`

Add the following to your existing requirements:

```
gunicorn>=21.2.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.9
```

#### 4. `.env` file (for local testing, DO NOT commit)

```env
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883
MQTT_USER=
MQTT_PASSWORD=
DATABASE_URL=sqlite:///iot_data.db
PORT=8050
DEBUG=False
```

#### 5. `.gitignore`

```
__pycache__/
*.pyc
*.db
.env
venv/
.vscode/
iot_data.db
```

---

## 🚀 Option 1: AWS EC2 (Recommended)

### Step 1: Launch EC2 Instance

1. **Sign in to AWS Console**: [console.aws.amazon.com](https://console.aws.amazon.com)
2. **Navigate to EC2** → Click "Launch Instance"
3. **Configure Instance**:
   - **Name**: `iot-dashboard-server`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**: `t2.micro` (1 GB RAM, free tier)
   - **Key Pair**: Create new or use existing
   - **Security Group**: Configure ports:
     - SSH (22) - Your IP only
     - HTTP (80) - Anywhere
     - HTTPS (443) - Anywhere
     - Custom TCP (8050) - Anywhere (for dashboard)
     - Custom TCP (1883) - Anywhere (if hosting MQTT broker)

4. **Launch Instance** and download the `.pem` key file

### Step 2: Connect to EC2 Instance

```bash
# Make key file private
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Git
sudo apt install git -y

# Install Nginx (optional, for reverse proxy)
sudo apt install nginx -y
```

### Step 4: Deploy Application

```bash
# Create application directory
mkdir ~/iot-dashboard
cd ~/iot-dashboard

# Clone or upload your code (option 1: using git)
git clone <your-repo-url> .

# OR upload files using SCP (option 2: from local machine)
# scp -i your-key.pem -r "C:\Users\Khalamullah\Desktop\IOT DASHBOARD\*" ubuntu@your-ec2-ip:~/iot-dashboard/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
nano .env
# Add your environment variables
```

### Step 5: Configure as System Service

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/iot-dashboard.service
```

Add the following content:

```ini
[Unit]
Description=IoT Dashboard Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/iot-dashboard
Environment="PATH=/home/ubuntu/iot-dashboard/venv/bin"
ExecStart=/home/ubuntu/iot-dashboard/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8050 dashboard_multidevice:server
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable iot-dashboard
sudo systemctl start iot-dashboard
sudo systemctl status iot-dashboard
```

### Step 6: Configure Nginx Reverse Proxy (Optional but Recommended)

```bash
sudo nano /etc/nginx/sites-available/iot-dashboard
```

Add configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or your EC2 public IP

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/iot-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Access Your Dashboard

Visit: `http://your-ec2-public-ip` or `http://your-domain.com`

---

## 🌐 Option 2: Google Cloud Platform

### Step 1: Create VM Instance

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Compute Engine** → **VM Instances**
3. Click **Create Instance**:
   - **Name**: `iot-dashboard`
   - **Region**: Choose closest to your location
   - **Machine type**: `e2-micro` (free tier)
   - **Boot disk**: Ubuntu 22.04 LTS
   - **Firewall**: Allow HTTP and HTTPS traffic

### Step 2: Configure Firewall Rules

```bash
# Create firewall rule for dashboard port
gcloud compute firewall-rules create allow-dashboard \
    --allow tcp:8050 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow dashboard access"
```

### Step 3: Connect and Deploy

```bash
# Connect via SSH (from GCP console or gcloud CLI)
gcloud compute ssh iot-dashboard

# Follow the same deployment steps as AWS EC2 (Steps 3-6)
```

---

## ☁️ Option 3: Microsoft Azure

### Step 1: Create Virtual Machine

1. Go to [Azure Portal](https://portal.azure.com)
2. Create **Virtual Machine**:
   - **VM name**: `iot-dashboard`
   - **Image**: Ubuntu Server 22.04 LTS
   - **Size**: `B1s` (free tier eligible)
   - **Authentication**: SSH public key
   - **Inbound ports**: 22, 80, 443, 8050

### Step 2: Deploy Application

```bash
# Connect via SSH
ssh azureuser@your-vm-ip

# Follow AWS EC2 deployment steps (Steps 3-6)
```

---

## 🎈 Option 4: Heroku (Easiest)

### Prerequisites

- Heroku account: [signup.heroku.com](https://signup.heroku.com)
- Heroku CLI installed: [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

### Step 1: Prepare Application

Modify `dashboard_multidevice.py` to use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Update configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'broker.hivemq.com')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
DB_PATH = os.getenv('DATABASE_URL', 'iot_data.db')

# Add server variable for Gunicorn
server = app.server

# Update main block
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8050))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run_server(debug=debug, host='0.0.0.0', port=port)
```

### Step 2: Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-iot-dashboard

# Set environment variables
heroku config:set MQTT_BROKER=broker.hivemq.com
heroku config:set MQTT_PORT=1883
heroku config:set DEBUG=False

# Initialize git (if not already)
git init
git add .
git commit -m "Initial deployment"

# Deploy
git push heroku main

# Open your app
heroku open
```

### Step 3: View Logs

```bash
heroku logs --tail
```

---

## 🚂 Option 5: Railway (Modern & Simple)

### Step 1: Sign Up

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub

### Step 2: Deploy from GitHub

1. **Create GitHub Repository**:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway auto-detects Python and deploys

### Step 3: Configure Environment Variables

In Railway dashboard:

- Go to **Variables** tab
- Add:
  - `MQTT_BROKER`: `broker.hivemq.com`
  - `MQTT_PORT`: `1883`
  - `PORT`: `8050`

### Step 4: Access Your App

Railway provides a public URL automatically: `https://your-app.railway.app`

---

## 📡 MQTT Broker Setup

### Option A: Use Public Broker (Testing Only)

```python
MQTT_BROKER = "broker.hivemq.com"  # Free public broker
MQTT_PORT = 1883
```

> ⚠️ **Warning**: Public brokers are NOT secure for production!

### Option B: Host Your Own Mosquitto Broker

#### On AWS EC2/GCP/Azure:

```bash
# Install Mosquitto
sudo apt install mosquitto mosquitto-clients -y

# Enable and start service
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Configure authentication
sudo nano /etc/mosquitto/mosquitto.conf
```

Add to config:

```conf
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
```

Create user:

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd iot_user
sudo systemctl restart mosquitto
```

Update dashboard configuration:

```python
MQTT_BROKER = "your-server-ip"
MQTT_PORT = 1883
MQTT_USER = "iot_user"
MQTT_PASSWORD = "your_password"
```

### Option C: Use Cloud MQTT Service

**CloudMQTT** (now part of CloudAMQP):

- [cloudamqp.com](https://www.cloudamqp.com)
- Free tier available
- Managed service

**HiveMQ Cloud**:

- [hivemq.com/mqtt-cloud-broker](https://www.hivemq.com/mqtt-cloud-broker/)
- Free tier: 100 connections
- Professional support

---

## 💾 Database Configuration

### Option A: SQLite (Default, Simple)

- Works out of the box
- Good for small deployments
- File-based storage

### Option B: PostgreSQL (Production)

#### On Heroku:

```bash
# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Get database URL
heroku config:get DATABASE_URL
```

#### On Railway:

- Add PostgreSQL plugin from dashboard
- Connection string auto-configured

#### Update Code:

```python
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///iot_data.db')

# For PostgreSQL
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
```

---

## 🔐 Security Best Practices

### 1. Use Environment Variables

Never hardcode credentials:

```python
import os
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
```

### 2. Enable HTTPS

#### Using Let's Encrypt (Free SSL):

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 3. Secure MQTT with TLS

```python
import ssl

mqtt_client.tls_set(
    ca_certs="/path/to/ca.crt",
    certfile="/path/to/client.crt",
    keyfile="/path/to/client.key",
    tls_version=ssl.PROTOCOL_TLSv1_2
)
mqtt_client.connect(MQTT_BROKER, 8883)  # Use port 8883 for TLS
```

### 4. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 8050/tcp # Dashboard
sudo ufw enable
```

### 5. Regular Updates

```bash
# Set up automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📊 Monitoring & Maintenance

### 1. Application Logs

```bash
# View systemd service logs
sudo journalctl -u iot-dashboard -f

# Heroku logs
heroku logs --tail

# Railway logs
# Available in Railway dashboard
```

### 2. System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop -y

# Check resource usage
htop
```

### 3. Database Backup

```bash
# Backup SQLite database
cp iot_data.db iot_data_backup_$(date +%Y%m%d).db

# Automated backup script
echo "0 2 * * * cp ~/iot-dashboard/iot_data.db ~/backups/iot_data_\$(date +\%Y\%m\%d).db" | crontab -
```

### 4. Uptime Monitoring

Use services like:

- **UptimeRobot**: [uptimerobot.com](https://uptimerobot.com) (Free)
- **Pingdom**: [pingdom.com](https://www.pingdom.com)
- **StatusCake**: [statuscake.com](https://www.statuscake.com)

---

## 🎯 Quick Start Recommendations

### For Beginners:

1. **Railway** - Easiest deployment, free tier
2. Use public MQTT broker initially
3. SQLite database

### For Production:

1. **AWS EC2** - Full control and scalability
2. Self-hosted Mosquitto with TLS
3. PostgreSQL database
4. Nginx reverse proxy with HTTPS

### For Enterprise:

1. **AWS/Azure/GCP** with load balancing
2. Managed MQTT service (HiveMQ Cloud)
3. Managed PostgreSQL (RDS/Cloud SQL)
4. CDN and DDoS protection

---

## 🆘 Troubleshooting

### Dashboard won't start

```bash
# Check logs
sudo journalctl -u iot-dashboard -n 50

# Check if port is in use
sudo lsof -i :8050

# Restart service
sudo systemctl restart iot-dashboard
```

### MQTT connection fails

```bash
# Test MQTT broker
mosquitto_sub -h broker.hivemq.com -t "test/topic" -v

# Check firewall
sudo ufw status
```

### Database errors

```bash
# Check database file permissions
ls -la iot_data.db

# Reset database
rm iot_data.db
# Restart application to recreate
```

---

## 📚 Additional Resources

- **Dash Deployment**: [dash.plotly.com/deployment](https://dash.plotly.com/deployment)
- **MQTT Security**: [mqtt.org/mqtt-security-fundamentals](https://mqtt.org/mqtt-security-fundamentals/)
- **AWS EC2 Guide**: [docs.aws.amazon.com/ec2](https://docs.aws.amazon.com/ec2/)
- **Heroku Python**: [devcenter.heroku.com/articles/getting-started-with-python](https://devcenter.heroku.com/articles/getting-started-with-python)

---

**Need Help?** Review the deployment logs and check the troubleshooting section. For platform-specific issues, consult the respective cloud provider's documentation.

**Good luck with your deployment! 🚀**
