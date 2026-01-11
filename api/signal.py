import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timezone
import ta

def get_signal():
    """Generate a simple trading signal without ML model"""
    try:
        # Fetch recent data
        ticker = yf.Ticker("GC=F")  # Gold futures
        df = ticker.history(period="5d", interval="1h")
        
        if df.empty:
            return None
        
        # Calculate indicators
        df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
        df['EMA_20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()
        df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
        
        # Get latest values
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Simple signal logic
        signal = 0  # Neutral
        confidence = 0.5
        
        # Buy conditions
        if (latest['Close'] > latest['EMA_20'] and 
            latest['RSI'] < 70 and latest['RSI'] > 50 and
            latest['Close'] > prev['Close']):
            signal = 1
            confidence = 0.75
        
        # Sell conditions
        elif (latest['Close'] < latest['EMA_20'] and 
              latest['RSI'] > 30 and latest['RSI'] < 50 and
              latest['Close'] < prev['Close']):
            signal = 2
            confidence = 0.75
        
        # Calculate SL/TP
        entry_price = latest['Close']
        atr = latest['ATR']
        
        if signal == 1:  # Buy
            sl = entry_price - (2 * atr)
            tp = entry_price + (4 * atr)
        elif signal == 2:  # Sell
            sl = entry_price + (2 * atr)
            tp = entry_price - (4 * atr)
        else:
            sl = tp = None
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'signal': signal,
            'confidence': confidence,
            'entry_price': float(entry_price),
            'stop_loss': float(sl) if sl else None,
            'take_profit': float(tp) if tp else None,
            'atr': float(atr),
            'session': 'Live',
            'rsi': float(latest['RSI']),
            'adx': 25.0  # Placeholder
        }
        
    except Exception as e:
        print(f"Error generating signal: {e}")
        return None

def handler(request):
    """Vercel serverless function handler"""
    signal = get_signal()
    
    if signal:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': {'success': True, 'signal': signal}
        }
    else:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': {'success': False, 'message': 'No signal generated'}
        }