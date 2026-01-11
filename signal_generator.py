import pandas as pd
import numpy as np
import joblib
import time
from datetime import datetime, timezone, timedelta
from processor import DataProcessor
from performance_monitor import PerformanceMonitor

class SignalGenerator:
    def __init__(self, model_path='gold_v1.joblib'):
        self.model = joblib.load(model_path)
        self.processor = DataProcessor()
        self.performance_monitor = PerformanceMonitor()
        self.confidence_threshold = 0.70  # Improved: 70% instead of 75%
        
    def get_current_session(self):
        """Determine current trading session"""
        now_gmt = datetime.now(timezone.utc)
        hour = now_gmt.hour
        
        if 8 <= hour < 16:
            if 13 <= hour < 16:
                return "London/NY Overlap"
            else:
                return "London Session"
        elif 13 <= hour < 21:
            return "New York Session"
        else:
            return "Asian Session"
    
    def calculate_sl_tp(self, signal, entry_price, atr):
        """Calculate Stop Loss and Take Profit levels with improved dynamic ATR"""
        # Improved dynamic ATR multipliers
        if atr > 20:  # High volatility
            sl_mult, tp_mult = 2.5, 5.0
        elif atr > 15:  # Medium volatility
            sl_mult, tp_mult = 2.0, 4.0
        else:  # Low volatility
            sl_mult, tp_mult = 1.5, 3.0
            
        if signal == 1:  # Buy
            sl = entry_price - (sl_mult * atr)
            tp = entry_price + (tp_mult * atr)
        elif signal == 2:  # Sell
            sl = entry_price + (sl_mult * atr)
            tp = entry_price - (tp_mult * atr)
        else:
            sl = tp = None
            
        return sl, tp
    
    def generate_signal(self):
        """Generate trading signal for current market conditions"""
        try:
            # Check if signals are allowed based on performance
            if not self.performance_monitor.is_signal_allowed():
                print("🔴 SIGNALS SUSPENDED - Poor performance detected")
                print(self.performance_monitor.get_performance_report())
                return None
            
            # Get latest data
            df = self.processor.fetch_data(period="1mo")  # Last month for recent data
            df = self.processor.add_indicators(df)
            df = self.processor.add_session_flags(df)
            
            # Get latest row
            latest = df.iloc[-1]
            
            # Prepare features
            feature_cols = self.processor.get_features(df)
            X = df[feature_cols].iloc[-1:].fillna(0)
            
            # Get prediction and probabilities
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            
            # Get confidence (max probability)
            confidence = np.max(probabilities)
            
            # Apply confidence gate
            if confidence < self.confidence_threshold:
                return None
            
            # Calculate SL/TP
            entry_price = latest['Close']
            atr = latest['ATR']
            sl, tp = self.calculate_sl_tp(prediction, entry_price, atr)
            
            # Create signal dictionary
            signal = {
                'timestamp': latest.name,
                'signal': prediction,
                'confidence': confidence,
                'entry_price': entry_price,
                'stop_loss': sl,
                'take_profit': tp,
                'atr': atr,
                'session': self.get_current_session(),
                'rsi': latest['RSI'],
                'adx': latest['ADX']
            }
            
            return signal
            
        except Exception as e:
            print(f"Error generating signal: {e}")
            return None
    
    def print_trade_ticket(self, signal):
        """Print detailed trade ticket"""
        signal_names = {0: "NEUTRAL", 1: "BUY", 2: "SELL"}
        
        print("\n" + "="*50)
        print("           GOLD TRADE TICKET")
        print("="*50)
        print(f"Timestamp:     {signal['timestamp']}")
        print(f"Session:       {signal['session']}")
        print(f"Signal:        {signal_names[signal['signal']]}")
        print(f"Confidence:    {signal['confidence']:.1%}")
        print(f"Entry Price:   ${signal['entry_price']:.2f}")
        
        if signal['signal'] != 0:
            print(f"Stop Loss:     ${signal['stop_loss']:.2f}")
            print(f"Take Profit:   ${signal['take_profit']:.2f}")
            risk_reward = abs(signal['take_profit'] - signal['entry_price']) / abs(signal['entry_price'] - signal['stop_loss'])
            print(f"Risk/Reward:   1:{risk_reward:.1f}")
        
        print(f"ATR:           ${signal['atr']:.2f}")
        print(f"RSI:           {signal['rsi']:.1f}")
        print(f"ADX:           {signal['adx']:.1f}")
        print("="*50)
    
    def run_live_loop(self, check_interval=3600):
        """Run live signal generation loop synced to top of hour"""
        print("Starting Gold AI Signal Generator...")
        print(f"Confidence threshold: {self.confidence_threshold:.0%}")
        print("IMPROVED SYSTEM: 8H predictions + Dynamic ATR + 70% confidence")
        
        # Calculate time until next hour
        now = datetime.now()
        minutes_to_next_hour = 60 - now.minute
        seconds_to_next_hour = (minutes_to_next_hour * 60) - now.second
        
        print(f"Syncing to next hour in {minutes_to_next_hour} minutes...")
        if minutes_to_next_hour < 60:
            time.sleep(seconds_to_next_hour)
        
        last_signal_hour = None
        
        while True:
            try:
                current_hour = datetime.now().hour
                print(f"\n[{datetime.now()}] Checking market...")
                
                signal = self.generate_signal()
                
                # Only show new signals (avoid duplicates)
                if signal and signal['signal'] != 0 and current_hour != last_signal_hour:
                    self.print_trade_ticket(signal)
                    last_signal_hour = current_hour
                else:
                    if signal:
                        if current_hour == last_signal_hour:
                            print("Same hour - no new signal")
                        else:
                            print(f"NEUTRAL signal (Confidence: {signal['confidence']:.1%})")
                    else:
                        print("No signal generated (Low confidence)")
                
                print(f"Next check at {(datetime.now() + timedelta(hours=1)).strftime('%H:00')}")
                time.sleep(3600)  # Always wait exactly 1 hour
                
            except KeyboardInterrupt:
                print("\nSignal generator stopped by user.")
                break
            except Exception as e:
                print(f"Error in live loop: {e}")
                time.sleep(60)  # Wait 1 minute before retry

if __name__ == "__main__":
    try:
        generator = SignalGenerator()
        
        # Generate single signal for testing
        print("Testing signal generation...")
        signal = generator.generate_signal()
        if signal:
            generator.print_trade_ticket(signal)
        
        # Ask user if they want to run live loop
        response = input("\nRun live signal generator? (y/n): ")
        if response.lower() == 'y':
            generator.run_live_loop()
            
    except FileNotFoundError:
        print("Model file 'gold_v1.joblib' not found. Please run model_trainer.py first.")