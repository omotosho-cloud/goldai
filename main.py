"""
Gold AI Signal Generator - Main Execution Script
Professional-grade AI system for XAU/USD trading signals
"""

from processor import DataProcessor
from model_trainer import ModelTrainer
from signal_generator import SignalGenerator
from monthly_retrainer import MonthlyRetrainer
from performance_monitor import PerformanceMonitor
from trade_tracker import TradeTracker
import os

def main():
    print("="*60)
    print("        GOLD AI SIGNAL GENERATOR v1.0")
    print("="*60)
    
    # Check if model exists
    model_exists = os.path.exists('gold_v1.joblib')
    
    if not model_exists:
        print("\n1. Training new model...")
        trainer = ModelTrainer()
        trainer.train_model()
        trainer.evaluate_model()
    else:
        print("\nUsing existing model: gold_v1.joblib")
        print("(Run 'python model_trainer.py' to retrain manually)")
    
    print("\n2. Starting signal generator...")
    generator = SignalGenerator()
    
    # Test signal generation
    print("\nTesting signal generation...")
    signal = generator.generate_signal()
    if signal:
        generator.print_trade_ticket(signal)
    else:
        print("No signal generated (market conditions not met)")
    
    # Option to run live
    print("\nOptions:")
    print("1. Run live signal generator (checks every hour)")
    print("2. Generate single signal and exit")
    print("3. Run backtest (see historical P/L)")
    print("4. Start monthly retraining scheduler")
    print("5. Force retrain model now")
    print("6. Start trade monitoring")
    print("7. Show performance report")
    print("8. Exit")
    
    choice = input("\nSelect option (1-8): ")
    
    if choice == '1':
        generator.run_live_loop()
    elif choice == '2':
        signal = generator.generate_signal()
        if signal:
            generator.print_trade_ticket(signal)
        else:
            print("No signal generated")
    elif choice == '3':
        print("\nBacktest feature not available")
        print("Use final_comprehensive_tester.py for testing")
    elif choice == '4':
        print("\nStarting monthly retraining scheduler...")
        retrainer = MonthlyRetrainer()
        retrainer.start_scheduler()
    elif choice == '5':
        print("\nForcing model retrain...")
        retrainer = MonthlyRetrainer()
        retrainer.force_retrain()
    elif choice == '6':
        print("\nStarting trade monitoring...")
        tracker = TradeTracker()
        tracker.start_monitoring()
    elif choice == '7':
        print("\nPerformance Report:")
        monitor = PerformanceMonitor()
        print(monitor.get_performance_report())
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()