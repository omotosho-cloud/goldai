"""
Automated Trade Tracker for Gold AI System
Monitors trade outcomes and feeds performance data
"""

import json
import time
from datetime import datetime, timedelta
import yfinance as yf
from performance_monitor import PerformanceMonitor
import logging

class TradeTracker:
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.active_trades_file = 'active_trades.json'
        self.symbol = "GC=F"  # Gold futures
        
    def load_active_trades(self):
        """Load active trades from file"""
        try:
            with open(self.active_trades_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_active_trades(self, trades):
        """Save active trades to file"""
        with open(self.active_trades_file, 'w') as f:
            json.dump(trades, f, indent=2, default=str)
    
    def add_trade(self, signal):
        """Add new trade to tracking"""
        if signal['signal'] == 0:  # Skip neutral signals
            return
            
        trades = self.load_active_trades()
        
        trade = {
            'id': f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'signal': signal,
            'status': 'active',
            'entry_time': datetime.now().isoformat()
        }
        
        trades.append(trade)
        self.save_active_trades(trades)
        
        print(f"✅ Trade added to tracking: {trade['id']}")
        logging.info(f"Trade added to tracking: {trade['id']}")
    
    def get_current_price(self):
        """Get current gold price"""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period="1d", interval="1m")
            return data['Close'].iloc[-1] if not data.empty else None
        except:
            return None
    
    def check_trade_outcomes(self):
        """Check if any active trades have hit SL or TP"""
        trades = self.load_active_trades()
        current_price = self.get_current_price()
        
        if not current_price:
            print("Could not fetch current price")
            return
        
        updated_trades = []
        
        for trade in trades:
            if trade['status'] != 'active':
                updated_trades.append(trade)
                continue
                
            signal = trade['signal']
            entry_price = signal['entry_price']
            sl = signal['stop_loss']
            tp = signal['take_profit']
            
            result = None
            profit_loss = 0
            
            if signal['signal'] == 1:  # Buy trade
                if current_price <= sl:
                    result = 'loss'
                    profit_loss = sl - entry_price
                elif current_price >= tp:
                    result = 'win'
                    profit_loss = tp - entry_price
            elif signal['signal'] == 2:  # Sell trade
                if current_price >= sl:
                    result = 'loss'
                    profit_loss = entry_price - sl
                elif current_price <= tp:
                    result = 'win'
                    profit_loss = entry_price - tp
            
            if result:
                # Trade closed
                trade['status'] = 'closed'
                trade['result'] = result
                trade['profit_loss'] = profit_loss
                trade['exit_price'] = current_price
                trade['exit_time'] = datetime.now().isoformat()
                
                # Record in performance monitor
                self.performance_monitor.record_trade_result(signal, result, profit_loss)
                
                print(f"🎯 Trade closed: {trade['id']} - {result.upper()} (${profit_loss:.2f})")
                logging.info(f"Trade closed: {trade['id']} - {result} - P&L: ${profit_loss:.2f}")
            
            updated_trades.append(trade)
        
        self.save_active_trades(updated_trades)
    
    def check_time_based_exits(self, max_hours=24):
        """Close trades that have been open too long"""
        trades = self.load_active_trades()
        current_time = datetime.now()
        updated_trades = []
        
        for trade in trades:
            if trade['status'] != 'active':
                updated_trades.append(trade)
                continue
                
            entry_time = datetime.fromisoformat(trade['entry_time'])
            hours_open = (current_time - entry_time).total_seconds() / 3600
            
            if hours_open >= max_hours:
                # Force close due to time
                current_price = self.get_current_price()
                if current_price:
                    signal = trade['signal']
                    entry_price = signal['entry_price']
                    
                    if signal['signal'] == 1:  # Buy
                        profit_loss = current_price - entry_price
                    else:  # Sell
                        profit_loss = entry_price - current_price
                    
                    result = 'win' if profit_loss > 0 else 'loss' if profit_loss < 0 else 'breakeven'
                    
                    trade['status'] = 'closed'
                    trade['result'] = result
                    trade['profit_loss'] = profit_loss
                    trade['exit_price'] = current_price
                    trade['exit_time'] = current_time.isoformat()
                    trade['exit_reason'] = 'time_based'
                    
                    # Record in performance monitor
                    self.performance_monitor.record_trade_result(signal, result, profit_loss)
                    
                    print(f"⏰ Trade closed (time): {trade['id']} - {result.upper()} (${profit_loss:.2f})")
                    logging.info(f"Trade closed (time): {trade['id']} - {result} - P&L: ${profit_loss:.2f}")
            
            updated_trades.append(trade)
        
        self.save_active_trades(updated_trades)
    
    def get_active_trades_summary(self):
        """Get summary of active trades"""
        trades = self.load_active_trades()
        active = [t for t in trades if t['status'] == 'active']
        
        if not active:
            return "No active trades"
        
        summary = f"Active Trades: {len(active)}\n"
        for trade in active:
            signal = trade['signal']
            entry_time = datetime.fromisoformat(trade['entry_time'])
            hours_open = (datetime.now() - entry_time).total_seconds() / 3600
            
            summary += f"- {trade['id']}: {['NEUTRAL', 'BUY', 'SELL'][signal['signal']]} @ ${signal['entry_price']:.2f} ({hours_open:.1f}h)\n"
        
        return summary
    
    def start_monitoring(self, check_interval=300):  # Check every 5 minutes
        """Start continuous trade monitoring"""
        print("Starting trade monitoring...")
        print(f"Check interval: {check_interval} seconds")
        
        while True:
            try:
                self.check_trade_outcomes()
                self.check_time_based_exits()
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\nTrade monitoring stopped")
                break
            except Exception as e:
                print(f"Error in trade monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retry

if __name__ == "__main__":
    tracker = TradeTracker()
    
    print("Gold AI Trade Tracker")
    print("1. Start monitoring")
    print("2. Show active trades")
    print("3. Show performance report")
    
    choice = input("Select option (1-3): ")
    
    if choice == '1':
        tracker.start_monitoring()
    elif choice == '2':
        print(tracker.get_active_trades_summary())
    elif choice == '3':
        print(tracker.performance_monitor.get_performance_report())