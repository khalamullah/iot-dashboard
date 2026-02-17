# Quick Deployment Guide

This is a condensed version of the full deployment guide. For detailed instructions, see [CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md).

## 🚀 Fastest Deployment Options

### Option 1: Railway (Recommended for Beginners)

1. **Sign up**: [railway.app](https://railway.app)
2. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
3. **Deploy**: Click "New Project" → "Deploy from GitHub repo"
4. **Done!** Railway auto-detects and deploys

### Option 2: Heroku

```bash
# Install Heroku CLI, then:
heroku login
heroku create your-app-name
git push heroku main
heroku open
```

### Option 3: AWS EC2 (Production)

1. Launch Ubuntu EC2 instance
2. Upload files or clone from git
3. Run deployment script:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## 📝 Pre-Deployment Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test locally: `python dashboard_multidevice.py`
- [ ] Create `.env` file (copy from `.env.example`)
- [ ] Update MQTT broker settings
- [ ] Choose deployment platform

## 🔧 Required Files (Already Created)

- ✅ `Procfile` - Heroku/Railway configuration
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - Dependencies
- ✅ `.env.example` - Environment variables template
- ✅ `.gitignore` - Git exclusions
- ✅ `deploy.sh` - Automated deployment script

## 🌐 Access Your Dashboard

After deployment, your dashboard will be available at:

- **Railway**: `https://your-app.railway.app`
- **Heroku**: `https://your-app.herokuapp.com`
- **AWS/GCP/Azure**: `http://your-server-ip`

## 🔐 Important: Environment Variables

Set these on your platform:

| Variable      | Example             | Description         |
| ------------- | ------------------- | ------------------- |
| `MQTT_BROKER` | `broker.hivemq.com` | MQTT broker address |
| `MQTT_PORT`   | `1883`              | MQTT port           |
| `PORT`        | `8050`              | Dashboard port      |
| `DEBUG`       | `False`             | Debug mode          |

## 📚 Full Documentation

For detailed instructions, troubleshooting, and advanced configuration:

- [CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [README.md](README.md) - Project overview
- [DEVICE_SETUP.md](DEVICE_SETUP.md) - Device configuration

## 🆘 Quick Troubleshooting

**Dashboard won't start?**

```bash
# Check logs
heroku logs --tail  # Heroku
# or
sudo journalctl -u iot-dashboard -f  # Linux server
```

**MQTT not connecting?**

- Verify broker address in environment variables
- Check firewall rules
- Test with: `mosquitto_sub -h broker.hivemq.com -t "test/topic"`

## 🎯 Recommended Setup

**For Testing**: Railway + Public MQTT broker
**For Production**: AWS EC2 + Private Mosquitto + PostgreSQL

---

**Need help?** See the full guide: [CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md)
