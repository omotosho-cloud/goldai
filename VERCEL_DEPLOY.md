# Vercel Deployment Guide

## 🚀 Deploy to Vercel (Serverless)

### Quick Deploy:
1. Push code to GitHub
2. Connect to Vercel
3. Deploy automatically

### Manual Steps:

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

### ⚠️ Limitations in Serverless Mode:
- No persistent background processes
- No file system storage
- No WebSocket connections
- No continuous monitoring
- Simplified signal generation

### 🌟 What Works:
- ✅ Web dashboard
- ✅ Basic signal generation
- ✅ API endpoints
- ✅ Mobile-responsive design
- ✅ Real-time data fetching

### 📝 Environment Variables:
Set in Vercel dashboard if needed:
- `PYTHON_VERSION=3.9`

### 🔧 Files for Vercel:
- `vercel.json` - Configuration
- `api/index.py` - Main app
- `api/signal.py` - Signal generation
- `requirements-vercel.txt` - Dependencies

### 🚀 Alternative: Full-Featured Deployment
For complete functionality, use:
- **Railway**: `railway up`
- **Heroku**: `git push heroku main`
- **DigitalOcean**: Docker deployment
- **AWS EC2**: Full server deployment