"""
Gold AI Mobile API Client
Lightweight client for mobile access to trading signals
"""

import requests
import json
from datetime import datetime
import time

class GoldAIMobileClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_status(self):
        """Get system status"""
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_current_signal(self):
        """Get current trading signal"""
        try:
            response = self.session.get(f"{self.base_url}/api/signal/current")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_active_trades(self):
        """Get active trades"""
        try:
            response = self.session.get(f"{self.base_url}/api/trades/active")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_performance(self):
        """Get performance metrics"""
        try:
            response = self.session.get(f"{self.base_url}/api/performance")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def start_system(self):
        """Start the AI system"""
        try:
            response = self.session.post(f"{self.base_url}/api/system/start")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def stop_system(self):
        """Stop the AI system"""
        try:
            response = self.session.post(f"{self.base_url}/api/system/stop")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def retrain_model(self):
        """Trigger model retraining"""
        try:
            response = self.session.post(f"{self.base_url}/api/retrain")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def print_signal_summary(self, signal_data):
        """Print formatted signal summary"""
        if "error" in signal_data:
            print(f"❌ Error: {signal_data['error']}")
            return
        
        if not signal_data.get("success"):
            print("⚪ No signal available")
            return
        
        signal = signal_data["signal"]
        signal_names = {0: "NEUTRAL ⚪", 1: "BUY 🟢", 2: "SELL 🔴"}
        
        print("\n" + "="*40)
        print("📱 GOLD AI MOBILE SIGNAL")
        print("="*40)
        print(f"Signal: {signal_names.get(signal['signal'], 'UNKNOWN')}")
        print(f"Confidence: {signal['confidence']:.1%}")
        print(f"Entry: ${signal['entry_price']:.2f}")
        
        if signal['signal'] != 0:
            print(f"Stop Loss: ${signal['stop_loss']:.2f}")
            print(f"Take Profit: ${signal['take_profit']:.2f}")
        
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        print("="*40)
    
    def monitor_signals(self, interval=300):
        """Monitor signals continuously"""
        print("📱 Starting Gold AI Mobile Monitor")
        print(f"Checking every {interval//60} minutes...")
        
        while True:
            try:
                # Get current signal
                signal_data = self.get_current_signal()
                self.print_signal_summary(signal_data)
                
                # Get system status
                status = self.get_status()
                if status.get("running"):
                    print(f"✅ System: Running | Active Trades: {status.get('active_trades_count', 0)}")
                else:
                    print("🔴 System: Stopped")
                
                print(f"Next check in {interval//60} minutes...\n")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n📱 Mobile monitor stopped")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(60)

def main():
    """Mobile client main menu"""
    client = GoldAIMobileClient()
    
    print("📱 Gold AI Mobile Client")
    print("="*30)
    
    while True:
        print("\n1. Get Current Signal")
        print("2. Check System Status")
        print("3. View Active Trades")
        print("4. Performance Report")
        print("5. Start System")
        print("6. Stop System")
        print("7. Monitor Signals")
        print("8. Exit")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == '1':
            signal = client.get_current_signal()
            client.print_signal_summary(signal)
        
        elif choice == '2':
            status = client.get_status()
            if "error" not in status:
                print(f"\n📊 System Status: {status.get('system_status', 'unknown').upper()}")
                print(f"Running: {'✅' if status.get('running') else '❌'}")
                print(f"Active Trades: {status.get('active_trades_count', 0)}")
            else:
                print(f"❌ Error: {status['error']}")
        
        elif choice == '3':
            trades = client.get_active_trades()
            if trades.get("success") and trades.get("trades"):
                print(f"\n📈 Active Trades ({len(trades['trades'])})")
                for i, trade in enumerate(trades["trades"], 1):
                    signal_names = {1: "BUY 🟢", 2: "SELL 🔴"}
                    print(f"{i}. {signal_names.get(trade['signal'], 'UNKNOWN')} @ ${trade['entry_price']:.2f}")
            else:
                print("\n📈 No active trades")
        
        elif choice == '4':
            perf = client.get_performance()
            if perf.get("success"):
                metrics = perf.get("metrics", {})
                print(f"\n📊 Performance Report")
                print(f"Win Rate: {metrics.get('win_rate', 0):.1%}")
                print(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}")
                print(f"Total Trades: {metrics.get('total_trades', 0)}")
            else:
                print("❌ Error loading performance data")
        
        elif choice == '5':
            result = client.start_system()
            print(f"✅ {result.get('message', 'System start requested')}")
        
        elif choice == '6':
            result = client.stop_system()
            print(f"🔴 {result.get('message', 'System stop requested')}")
        
        elif choice == '7':
            client.monitor_signals()
        
        elif choice == '8':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()