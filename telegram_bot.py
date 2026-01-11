"""
Telegram Bot for Gold AI Notifications
Sends trading signals and alerts to Telegram
"""

import requests
import json
from datetime import datetime

class TelegramBot:
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or "YOUR_BOT_TOKEN"
        self.chat_id = chat_id or "YOUR_CHAT_ID"
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_message(self, message):
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def send_signal(self, signal):
        """Send trading signal notification"""
        signal_names = {0: "NEUTRAL", 1: "🟢 BUY", 2: "🔴 SELL"}
        
        if signal['signal'] != 0:
            message = f"""
🎯 <b>GOLD AI SIGNAL</b>
━━━━━━━━━━━━━━━━━━━━
Signal: <b>{signal_names[signal['signal']]}</b>
Confidence: <b>{signal['confidence']:.1%}</b>
Entry: <b>${signal['entry_price']:.2f}</b>
Stop Loss: <b>${signal['stop_loss']:.2f}</b>
Take Profit: <b>${signal['take_profit']:.2f}</b>
━━━━━━━━━━━━━━━━━━━━
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        else:
            message = f"""
⚪ <b>NEUTRAL SIGNAL</b>
Confidence: {signal['confidence']:.1%}
Time: {datetime.now().strftime('%H:%M:%S')}
"""
        
        return self.send_message(message)
    
    def send_performance_alert(self, status, metrics):
        """Send performance status alert"""
        emoji = "🟢" if status == "active" else "🔴"
        
        message = f"""
{emoji} <b>PERFORMANCE UPDATE</b>
━━━━━━━━━━━━━━━━━━━━
Status: <b>{status.upper()}</b>
Win Rate: <b>{metrics.get('win_rate', 0):.1%}</b>
Profit Factor: <b>{metrics.get('profit_factor', 0):.2f}</b>
Total Trades: <b>{metrics.get('total_trades', 0)}</b>
━━━━━━━━━━━━━━━━━━━━
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return self.send_message(message)

# Configuration
TELEGRAM_CONFIG = {
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "chat_id": "YOUR_CHAT_ID_HERE",
    "enabled": False  # Set to True to enable notifications
}

if __name__ == "__main__":
    print("Telegram Bot Setup:")
    print("1. Create bot with @BotFather on Telegram")
    print("2. Get bot token")
    print("3. Get your chat ID")
    print("4. Update TELEGRAM_CONFIG")
    print("5. Set enabled=True")