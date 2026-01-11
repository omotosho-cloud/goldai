"""
Monthly Model Retrainer for Gold AI System
Automatically retrains the model on the first day of each month
"""

import schedule
import time
import os
from datetime import datetime, timedelta
from model_trainer import ModelTrainer
from performance_monitor import PerformanceMonitor
from telegram_bot import TelegramBot, TELEGRAM_CONFIG
import logging

class MonthlyRetrainer:
    def __init__(self):
        self.trainer = ModelTrainer()
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize Telegram bot if enabled
        if TELEGRAM_CONFIG.get('enabled', False):
            self.telegram_bot = TelegramBot(
                TELEGRAM_CONFIG.get('bot_token'),
                TELEGRAM_CONFIG.get('chat_id')
            )
        else:
            self.telegram_bot = None
            
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for retraining events"""
        logging.basicConfig(
            filename='retrain_log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def retrain_model(self):
        """Retrain the model and backup old version"""
        try:
            print(f"\n{'='*60}")
            print(f"MONTHLY RETRAINING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            # Backup existing model
            if os.path.exists('gold_v1.joblib'):
                backup_name = f"gold_v1_backup_{datetime.now().strftime('%Y%m%d')}.joblib"
                os.rename('gold_v1.joblib', backup_name)
                print(f"Backed up existing model as: {backup_name}")
                logging.info(f"Backed up model as: {backup_name}")
            
            # Train new model
            print("Starting monthly retraining...")
            self.trainer.train_model()
            self.trainer.evaluate_model()
            
            # Set model to testing mode after retrain
            status = self.performance_monitor.post_retrain_validation()
            
            # Send Telegram notification about retraining
            if self.telegram_bot:
                message = f"🔄 <b>MODEL RETRAINED</b>\nStatus: {status.upper()}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.telegram_bot.send_message(message)
            
            print("Monthly retraining completed successfully!")
            print("Model is now in TESTING mode - signals suspended until performance validation")
            logging.info("Monthly retraining completed successfully - Model in testing mode")
            
        except Exception as e:
            error_msg = f"Monthly retraining failed: {str(e)}"
            print(error_msg)
            logging.error(error_msg)
            
            # Restore backup if training failed
            backup_files = [f for f in os.listdir('.') if f.startswith('gold_v1_backup_')]
            if backup_files:
                latest_backup = max(backup_files)
                os.rename(latest_backup, 'gold_v1.joblib')
                print(f"Restored backup model: {latest_backup}")
                logging.info(f"Restored backup model: {latest_backup}")
    
    def start_scheduler(self):
        """Start the monthly retraining scheduler"""
        from datetime import datetime
        import os
        
        def check_monthly():
            now = datetime.now()
            # Check if it's the 1st day of the month and we haven't retrained yet
            if now.day == 1:
                retrain_flag = f"retrained_{now.strftime('%Y_%m')}.flag"
                if not os.path.exists(retrain_flag):
                    self.retrain_model()
                    # Create flag file to prevent multiple retrains in same month
                    with open(retrain_flag, 'w') as f:
                        f.write(f"Retrained on {now}")
        
        # Check every hour for the 1st day
        schedule.every().hour.do(check_monthly)
        
        print("Monthly retrainer started!")
        print("Model will retrain on the 1st of each month (anytime you're online)")
        print("Press Ctrl+C to stop the scheduler")
        
        logging.info("Monthly retrainer started")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(3600)  # Check every hour
        except KeyboardInterrupt:
            print("\nMonthly retrainer stopped")
            logging.info("Monthly retrainer stopped by user")
    
    def force_retrain(self):
        """Force immediate retraining (for testing)"""
        print("Forcing immediate retraining...")
        self.retrain_model()

if __name__ == "__main__":
    retrainer = MonthlyRetrainer()
    
    print("Gold AI Monthly Retrainer")
    print("1. Start monthly scheduler")
    print("2. Force retrain now")
    print("3. Exit")
    
    choice = input("Select option (1-3): ")
    
    if choice == '1':
        retrainer.start_scheduler()
    elif choice == '2':
        retrainer.force_retrain()
    else:
        print("Exiting...")