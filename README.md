# Gold AI Signal Generator App

Professional-grade AI system for XAU/USD (Gold) trading signals with modern web interface.

## 🚀 New Features - Version 2.0

- **Modern Web Dashboard**: Real-time web interface with live updates
- **Mobile API Client**: Access signals from any device
- **Real-time WebSocket Updates**: Live signal notifications
- **Performance Monitoring**: Advanced analytics and reporting
- **One-Click Deployment**: Easy setup with batch scripts
- **RESTful API**: Full API access for integrations
- **Responsive Design**: Works on desktop, tablet, and mobile

## 📊 Core Features

- **Hourly Predictions**: 1h timeframe analysis with 4h forward-looking labels
- **Multi-Class Classification**: Buy (1), Sell (2), Neutral (0) signals
- **Session Awareness**: London, New York, and Overlap session detection
- **Risk Management**: Dynamic SL/TP levels based on ATR
- **Confidence Gating**: Only signals with >70% confidence
- **Technical Indicators**: RSI, MACD, EMA, ATR, ADX, Bollinger Bands
- **Monthly Retraining**: Automatic model retraining on the 1st of each month
- **Performance Monitoring**: Continuous performance validation and signal control
- **Automatic Trade Tracking**: Real-time trade outcome monitoring
- **Signal Suspension**: Automatic signal suspension during poor performance

## 🧪 Integration Status

✅ **Core Components**
- Web Dashboard with real-time updates
- RESTful API endpoints
- Mobile client access
- Fallback signal generation
- Error handling and graceful degradation

✅ **Deployment Ready**
- Railway deployment configured
- Docker containerization
- Environment variable support
- Health checks and monitoring

✅ **Testing**
```bash
# Run integration tests
python test_integration.py
```

## 🎯 Quick Start

### Option 1: One-Click Start (Windows)
```bash
# Double-click or run:
start_app.bat
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start web application
python app.py

# 3. Open browser to:
http://localhost:5000
```

### Option 3: Mobile Client
```bash
# Access from mobile/remote device
python mobile_client.py
```

## 🌐 Web Dashboard

Access the modern web interface at `http://localhost:5000`

### Dashboard Features:
- **Real-time Signal Display**: Live trading signals with confidence levels
- **Active Trade Monitoring**: Track all open positions
- **Performance Analytics**: Win rate, profit factor, and detailed metrics
- **System Control**: Start/stop system with one click
- **Model Management**: Force retrain models when needed
- **Live Updates**: WebSocket-powered real-time updates

### API Endpoints:
- `GET /api/status` - System status
- `GET /api/signal/current` - Current trading signal
- `GET /api/trades/active` - Active trades
- `GET /api/performance` - Performance metrics
- `POST /api/system/start` - Start system
- `POST /api/system/stop` - Stop system
- `POST /api/retrain` - Force model retrain

## 📱 Mobile Access

Use the mobile client for remote access:

```python
from mobile_client import GoldAIMobileClient

client = GoldAIMobileClient("http://your-server:5000")
signal = client.get_current_signal()
client.print_signal_summary(signal)
```

## 🏗️ Architecture

```
Gold AI App/
├── app.py                 # Flask web application
├── templates/
│   └── dashboard.html     # Web dashboard
├── static/
│   ├── css/dashboard.css  # Styling
│   └── js/dashboard.js    # Frontend logic
├── mobile_client.py       # Mobile API client
├── signal_generator.py    # Core signal generation
├── trade_tracker.py       # Trade monitoring
├── performance_monitor.py # Performance analytics
├── integrated_goldai.py   # Complete system integration
└── config.json           # Configuration settings
```

## 🔧 Configuration

Edit `config.json` to customize:

- **Trading Parameters**: Confidence threshold, risk levels
- **Notifications**: Telegram, email alerts
- **Performance Thresholds**: Win rate, profit factor limits
- **UI Settings**: Theme, refresh rates, indicators
- **Model Settings**: Retraining schedule, backup options

## 📈 Signal Logic

**Buy Signal (1)**: Price increases +1% in 4h AND ADX > 20
**Sell Signal (2)**: Price decreases -1% in 4h AND ADX > 20  
**Neutral (0)**: ADX < 20 OR price within ±1% range

## 🛡️ Risk Management

- **Buy**: SL = Entry - (2×ATR), TP = Entry + (4×ATR)
- **Sell**: SL = Entry + (2×ATR), TP = Entry - (4×ATR)
- **Risk/Reward**: 1:2 ratio
- **Dynamic ATR**: Adjusts based on market volatility

## 📊 Performance Monitoring

### Automatic Performance Validation:
- **Schedule**: Continuous monitoring with 4-hour reports
- **Thresholds**: Min 55% win rate, 1.2 profit factor
- **Signal Control**: Auto-suspend signals if performance drops
- **Testing Mode**: New models validated before activation
- **Backup & Recovery**: Automatic rollback on failures

### Performance Metrics:
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Total Trades**: Number of completed trades
- **Active Trades**: Currently open positions
- **Signal Status**: Active/Suspended/Testing

## 🔄 Monthly Retraining

Automated model retraining system:
- **Schedule**: 1st of each month at 2:00 AM
- **Validation**: Performance testing before deployment
- **Backup**: Previous models saved automatically
- **Rollback**: Automatic revert if new model fails
- **Manual Override**: Force retrain via web interface

## 🚀 Deployment Options

### Local Development
```bash
python app.py
```

### Production (with Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 📱 Usage Examples

### Web Dashboard
1. Open `http://localhost:5000`
2. Click "Start System" to begin signal generation
3. Monitor real-time signals and performance
4. View active trades and analytics

### Mobile Client
```python
# Quick signal check
client = GoldAIMobileClient()
signal = client.get_current_signal()
client.print_signal_summary(signal)

# Continuous monitoring
client.monitor_signals(interval=300)  # Check every 5 minutes
```

### API Integration
```python
import requests

# Get current signal
response = requests.get('http://localhost:5000/api/signal/current')
signal = response.json()

# Start system
requests.post('http://localhost:5000/api/system/start')
```

## 🔧 Troubleshooting

### Common Issues:

1. **Model not found**: Run `python model_trainer.py` first
2. **Port already in use**: Change port in `config.json`
3. **Data fetch errors**: Check internet connection
4. **Performance issues**: Reduce update frequency in config

### Logs and Debugging:
- Check console output for errors
- Review `retrain_log.txt` for model issues
- Monitor `paper_trading.log` for trade tracking

## 📞 Support

For issues and feature requests:
1. Check the troubleshooting section
2. Review log files for error details
3. Ensure all dependencies are installed
4. Verify configuration settings

## 🔮 Roadmap

- [ ] Multi-timeframe analysis
- [ ] Additional currency pairs
- [ ] Advanced charting integration
- [ ] Machine learning model ensemble
- [ ] Cloud deployment templates
- [ ] Advanced notification systems
- [ ] Portfolio management features