# Railway Deployment Guide

## 🚀 Deploy Gold AI to Railway (Full Features)

### Method 1: One-Click Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

### Method 2: GitHub Integration

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/goldai.git
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway auto-detects Python and deploys

### Method 3: Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Deploy**:
   ```bash
   railway up
   ```

## ✅ What Works on Railway:

- ✅ **Full ML Model**: Complete AI signal generation
- ✅ **Background Processes**: Continuous monitoring
- ✅ **File Storage**: Persistent model and data files
- ✅ **WebSocket**: Real-time updates
- ✅ **Trade Tracking**: Complete trade monitoring
- ✅ **Performance Analytics**: Full reporting
- ✅ **Auto Retraining**: Monthly model updates
- ✅ **All Features**: Complete functionality

## 🔧 Environment Variables (Optional):

Set in Railway dashboard:
- `TELEGRAM_BOT_TOKEN` - For notifications
- `TELEGRAM_CHAT_ID` - For notifications
- `PYTHON_VERSION` - 3.9 (auto-detected)

## 📊 After Deployment:

1. **Access Dashboard**: `https://your-app.railway.app`
2. **Start System**: Click "Start System" in dashboard
3. **Monitor Signals**: Real-time updates
4. **Mobile Access**: Use mobile client with your Railway URL

## 💰 Railway Pricing:

- **Hobby Plan**: $5/month (recommended)
- **Pro Plan**: $20/month (for heavy usage)
- **Free Tier**: 500 hours/month (limited)

## 🚀 Deployment Files:

- `railway.json` - Railway configuration
- `Procfile` - Start command
- `requirements.txt` - Dependencies
- `app.py` - Main application (Railway-ready)

## 🔧 Troubleshooting:

1. **Build Fails**: Check requirements.txt
2. **App Crashes**: Check logs in Railway dashboard
3. **Port Issues**: Railway auto-assigns PORT
4. **Model Training**: First run may take 5-10 minutes

## 📱 Mobile Access:

```python
from mobile_client import GoldAIMobileClient

# Use your Railway URL
client = GoldAIMobileClient("https://your-app.railway.app")
signal = client.get_current_signal()
client.print_signal_summary(signal)
```

## 🎯 Next Steps:

1. Deploy to Railway
2. Access your dashboard
3. Start the AI system
4. Monitor live signals
5. Track performance
6. Enjoy automated trading signals!

**Railway gives you the COMPLETE Gold AI experience with zero local setup required!**