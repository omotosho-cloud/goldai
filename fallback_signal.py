"""
Fallback Signal Generator
Simple technical analysis-based signals when ML model is unavailable
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import ta

class FallbackSignalGenerator:
    def __init__(self):
        self.confidence_threshold = 0.60
        self.warning_shown = False
    
    def generate_signal(self):
        """Generate simple technical analysis signal with safety warnings"""
        if not self.warning_shown:
            print("⚠️  WARNING: Using fallback signals - ML model unavailable")
            print("⚠️  Fallback signals are less accurate than ML predictions")
            self.warning_shown = True
        
        try:
            # Fetch Gold data
            ticker = yf.Ticker("GC=F")
            df = ticker.history(period="5d", interval="1h")
            
            if df.empty or len(df) < 50:
                return None
            
            # Calculate indicators with null checks
            df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
            df['EMA_20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()
            df['EMA_50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
            df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
            
            # Drop rows with NaN values
            df = df.dropna()
            
            if len(df) < 2:
                return None
            
            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Validate data
            required_fields = ['Close', 'RSI', 'EMA_20', 'EMA_50', 'ATR']
            for field in required_fields:
                if pd.isna(latest[field]) or pd.isna(prev[field]):
                    return None
            
            # Conservative signal logic (higher threshold)
            signal = 0
            confidence = 0.5
            
            # Very strict buy conditions
            buy_conditions = [
                latest['Close'] > latest['EMA_20'],
                latest['EMA_20'] > latest['EMA_50'],
                latest['RSI'] > 55 and latest['RSI'] < 65,  # Stricter RSI range
                latest['Close'] > prev['Close'] * 1.001,  # Minimum 0.1% price increase
            ]
            
            # Very strict sell conditions  
            sell_conditions = [
                latest['Close'] < latest['EMA_20'],
                latest['EMA_20'] < latest['EMA_50'],
                latest['RSI'] < 45 and latest['RSI'] > 35,  # Stricter RSI range
                latest['Close'] < prev['Close'] * 0.999,  # Minimum 0.1% price decrease
            ]
            
            # Require ALL conditions (80% threshold)
            buy_score = sum(buy_conditions) / len(buy_conditions)
            sell_score = sum(sell_conditions) / len(sell_conditions)
            
            # Very conservative - require 80% of conditions
            if buy_score >= 0.8:
                signal = 1
                confidence = 0.65  # Lower max confidence for fallback
            elif sell_score >= 0.8:
                signal = 2
                confidence = 0.65  # Lower max confidence for fallback
            
            # Higher confidence threshold for fallback
            if confidence < 0.65:
                return None
            
            # Calculate conservative SL/TP
            entry_price = latest['Close']
            atr = latest['ATR']
            
            if signal == 1:  # Buy - tighter stops
                sl = entry_price - (1.5 * atr)  # Tighter stop loss
                tp = entry_price + (3 * atr)    # Conservative take profit
            elif signal == 2:  # Sell - tighter stops
                sl = entry_price + (1.5 * atr)  # Tighter stop loss
                tp = entry_price - (3 * atr)    # Conservative take profit
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
                'session': '⚠️ FALLBACK MODE - USE WITH CAUTION',
                'rsi': float(latest['RSI']),
                'adx': 25.0
            }
            
        except Exception as e:
            print(f"Fallback signal generation error: {e}")
            return None

if __name__ == "__main__":
    generator = FallbackSignalGenerator()
    signal = generator.generate_signal()
    if signal:
        print("Fallback Signal Generated:")
        print(f"Signal: {signal['signal']}")
        print(f"Confidence: {signal['confidence']:.1%}")
        print(f"Entry: ${signal['entry_price']:.2f}")
    else:
        print("No fallback signal generated")