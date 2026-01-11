"""
Integrated Gold AI System with Performance Monitoring
Combines signal generation with automatic trade tracking and performance validation
"""

from signal_generator import SignalGenerator
from trade_tracker import TradeTracker
from performance_monitor import PerformanceMonitor
from telegram_bot import TelegramBot, TELEGRAM_CONFIG
import time
from datetime import datetime, timedelta

class IntegratedGoldAI:
    def __init__(self):
        self.signal_generator = SignalGenerator()
        self.trade_tracker = TradeTracker()
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize Telegram bot if enabled
        if TELEGRAM_CONFIG.get('enabled', False):
            self.telegram_bot = TelegramBot(
                TELEGRAM_CONFIG.get('bot_token'),
                TELEGRAM_CONFIG.get('chat_id')
            )
            print("📱 Telegram notifications enabled")
        else:
            self.telegram_bot = None
            print("📱 Telegram notifications disabled")
        
    def run_complete_system(self):
        """Run the complete Gold AI system with performance monitoring"""
        print("🚀 Starting Integrated Gold AI System")
        print("Features: Signal Generation + Trade Tracking + Performance Monitoring")
        print(f"Confidence threshold: {self.signal_generator.confidence_threshold:.0%}")
        
        # Show current performance status
        print("\n" + "="*50)
        print("CURRENT PERFORMANCE STATUS")
        print("="*50)
        print(self.performance_monitor.get_performance_report())
        
        # Sync to next hour
        now = datetime.now()
        minutes_to_next_hour = 60 - now.minute
        seconds_to_next_hour = (minutes_to_next_hour * 60) - now.second
        
        if minutes_to_next_hour < 60:
            print(f"\\nSyncing to next hour in {minutes_to_next_hour} minutes...")
            time.sleep(seconds_to_next_hour)
        
        last_signal_hour = None
        
        while True:
            try:
                current_hour = datetime.now().hour
                print(f"\\n[{datetime.now()}] Checking market...")
                
                # Check existing trades first
                self.trade_tracker.check_trade_outcomes()
                self.trade_tracker.check_time_based_exits()
                
                # Generate new signal
                signal = self.signal_generator.generate_signal()
                
                if signal and signal['signal'] != 0 and current_hour != last_signal_hour:
                    # New trading signal
                    self.signal_generator.print_trade_ticket(signal)
                    
                    # Send Telegram notification
                    if self.telegram_bot:
                        self.telegram_bot.send_signal(signal)
                    
                    # Add to trade tracking
                    self.trade_tracker.add_trade(signal)
                    
                    last_signal_hour = current_hour
                    
                    # Show active trades summary
                    print("\\n" + "-"*30)
                    print("ACTIVE TRADES SUMMARY")
                    print("-"*30)
                    print(self.trade_tracker.get_active_trades_summary())
                    
                else:
                    if signal:
                        if current_hour == last_signal_hour:
                            print("Same hour - no new signal")
                        else:
                            print(f"NEUTRAL signal (Confidence: {signal['confidence']:.1%})")
                    else:
                        print("No signal generated")
                
                # Show performance status every 4 hours
                if current_hour % 4 == 0 and current_hour != last_signal_hour:
                    print("\\n" + "="*40)
                    print("PERFORMANCE UPDATE")
                    print("="*40)
                    report = self.performance_monitor.get_performance_report()
                    print(report)
                    
                    # Send Telegram performance update
                    if self.telegram_bot and "performance_metrics" in self.performance_monitor.load_performance_history():
                        data = self.performance_monitor.load_performance_history()
                        metrics = data.get('performance_metrics', {})
                        status = data.get('signal_status', 'unknown')
                        self.telegram_bot.send_performance_alert(status, metrics)
                
                print(f"Next check at {(datetime.now() + timedelta(hours=1)).strftime('%H:00')}")
                time.sleep(3600)  # Wait 1 hour
                
            except KeyboardInterrupt:
                print("\\n🛑 System stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in system: {e}")
                time.sleep(300)  # Wait 5 minutes before retry
    
    def get_system_status(self):
        """Get complete system status"""
        status = f"""
🎯 GOLD AI SYSTEM STATUS
========================

Signal Status: {'🟢 ACTIVE' if self.performance_monitor.is_signal_allowed() else '🔴 SUSPENDED'}

{self.performance_monitor.get_performance_report()}

{self.trade_tracker.get_active_trades_summary()}
"""
        return status

if __name__ == "__main__":
    system = IntegratedGoldAI()
    
    print("Integrated Gold AI System")
    print("1. Run complete system")
    print("2. Show system status")
    print("3. Exit")
    
    choice = input("Select option (1-3): ")
    
    if choice == '1':
        system.run_complete_system()
    elif choice == '2':
        print(system.get_system_status())
    else:
        print("Exiting...")