"""
Performance Monitor for Gold AI System
Tracks model performance and controls signal generation
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import numpy as np

class PerformanceMonitor:
    def __init__(self, performance_file='performance_history.json'):
        self.performance_file = performance_file
        self.min_win_rate = 0.55  # 55% minimum win rate
        self.min_profit_factor = 1.2  # 1.2 minimum profit factor
        self.min_trades_for_validation = 20  # Need 20 trades minimum
        self.performance_window_days = 30  # Evaluate last 30 days
        
    def load_performance_history(self):
        """Load performance history from file"""
        if os.path.exists(self.performance_file):
            with open(self.performance_file, 'r') as f:
                return json.load(f)
        return {
            'trades': [],
            'model_versions': [],
            'signal_status': 'active',  # active, suspended, testing
            'last_validation': None,
            'performance_metrics': {}
        }
    
    def save_performance_history(self, data):
        """Save performance history to file"""
        with open(self.performance_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def record_trade_result(self, signal, result, profit_loss):
        """Record trade result for performance tracking"""
        data = self.load_performance_history()
        
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'signal': signal['signal'],
            'confidence': signal['confidence'],
            'entry_price': signal['entry_price'],
            'result': result,  # 'win', 'loss', 'breakeven'
            'profit_loss': profit_loss,
            'model_version': self.get_current_model_version()
        }
        
        data['trades'].append(trade_record)
        self.save_performance_history(data)
        
        # Trigger performance validation after each trade
        self.validate_performance()
    
    def get_current_model_version(self):
        """Get current model version timestamp"""
        try:
            model_stat = os.stat('gold_v1.joblib')
            return datetime.fromtimestamp(model_stat.st_mtime).isoformat()
        except:
            return datetime.now().isoformat()
    
    def calculate_performance_metrics(self, trades):
        """Calculate key performance metrics"""
        if not trades:
            return None
            
        wins = [t for t in trades if t['result'] == 'win']
        losses = [t for t in trades if t['result'] == 'loss']
        
        total_trades = len(trades)
        win_rate = len(wins) / total_trades if total_trades > 0 else 0
        
        total_profit = sum(t['profit_loss'] for t in wins)
        total_loss = abs(sum(t['profit_loss'] for t in losses))
        
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        net_profit = sum(t['profit_loss'] for t in trades)
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'net_profit': net_profit,
            'avg_win': total_profit / len(wins) if wins else 0,
            'avg_loss': total_loss / len(losses) if losses else 0
        }
    
    def validate_performance(self):
        """Validate current model performance using only trades after last retrain"""
        data = self.load_performance_history()
        
        # Get current model version timestamp
        current_model_version = self.get_current_model_version()
        
        # Filter trades to only those after current model was created
        model_trades = [
            t for t in data['trades'] 
            if t.get('model_version') == current_model_version
        ]
        
        metrics = self.calculate_performance_metrics(model_trades)
        
        if not metrics or metrics['total_trades'] < self.min_trades_for_validation:
            # Not enough NEW model trades - keep current status
            logging.info(f"Insufficient NEW model trades for validation: {metrics['total_trades'] if metrics else 0}")
            return data['signal_status']
        
        # Check performance thresholds
        performance_ok = (
            metrics['win_rate'] >= self.min_win_rate and
            metrics['profit_factor'] >= self.min_profit_factor and
            metrics['net_profit'] > 0
        )
        
        # Update signal status
        if performance_ok:
            if data['signal_status'] in ['suspended', 'testing']:
                logging.info("NEW model performance validated - Activating signals")
                print("🟢 NEW MODEL VALIDATED - Signals activated")
            data['signal_status'] = 'active'
        else:
            if data['signal_status'] == 'active':
                logging.warning("NEW model performance poor - Suspending signals")
                print("🔴 NEW MODEL FAILED - Signals suspended")
            data['signal_status'] = 'suspended'
        
        # Update performance metrics
        data['performance_metrics'] = metrics
        data['last_validation'] = datetime.now().isoformat()
        
        self.save_performance_history(data)
        return data['signal_status']
    
    def is_signal_allowed(self):
        """Check if signals are currently allowed"""
        data = self.load_performance_history()
        return data.get('signal_status', 'active') == 'active'
    
    def get_performance_report(self):
        """Generate performance report"""
        data = self.load_performance_history()
        metrics = data.get('performance_metrics', {})
        
        if not metrics:
            return "No performance data available"
        
        status_emoji = "🟢" if data['signal_status'] == 'active' else "🔴"
        
        report = f"""
{status_emoji} PERFORMANCE STATUS: {data['signal_status'].upper()}

Recent Performance (Last 30 days):
- Total Trades: {metrics.get('total_trades', 0)}
- Win Rate: {metrics.get('win_rate', 0):.1%}
- Profit Factor: {metrics.get('profit_factor', 0):.2f}
- Net Profit: ${metrics.get('net_profit', 0):.2f}
- Avg Win: ${metrics.get('avg_win', 0):.2f}
- Avg Loss: ${metrics.get('avg_loss', 0):.2f}

Thresholds:
- Min Win Rate: {self.min_win_rate:.1%}
- Min Profit Factor: {self.min_profit_factor}
- Min Trades: {self.min_trades_for_validation}
"""
        return report
    
    def validate_new_model_on_historical_data(self):
        """Validate retrained model on recent historical data before going live"""
        try:
            from model_trainer import ModelTrainer
            from processor import DataProcessor
            
            # Get recent 3 months of data for out-of-sample testing
            processor = DataProcessor()
            df = processor.fetch_data(period="3mo")
            df = processor.add_indicators(df)
            df = processor.add_session_flags(df)
            df = processor.create_labels(df)
            
            # Try different time windows until we get enough trades
            test_periods = [720, 1440, 2160]  # 30, 60, 90 days of hourly data
            
            for test_size in test_periods:
                if test_size > len(df):
                    continue
                    
                test_df = df.iloc[-test_size:].copy()
            
            # Load current model and make predictions
            import joblib
            model = joblib.load('gold_v1.joblib')
            
            feature_cols = processor.get_features(test_df)
            X_test = test_df[feature_cols].fillna(0)
            predictions = model.predict(X_test)
            probabilities = model.predict_proba(X_test)
            
            # Simulate trading on historical data
            trades = []
            for i, (idx, row) in enumerate(test_df.iterrows()):
                pred = predictions[i]
                conf = np.max(probabilities[i])
                
                if pred != 0 and conf >= 0.70:  # Same confidence threshold
                    # Simulate trade outcome using actual future price movement
                    if i + 4 < len(test_df):  # Need 4h forward data
                        entry_price = row['Close']
                        future_price = test_df.iloc[i + 4]['Close']
                        
                        if pred == 1:  # Buy
                            profit_loss = future_price - entry_price
                        else:  # Sell
                            profit_loss = entry_price - future_price
                        
                        result = 'win' if profit_loss > 0 else 'loss'
                        trades.append({
                            'result': result,
                            'profit_loss': profit_loss,
                            'confidence': conf
                        })
            
                # Calculate performance metrics with recency weighting
                if len(trades) >= 10:
                    # Overall performance
                    overall_metrics = self.calculate_performance_metrics(trades)
                    
                    # Recent performance (last 1/3 of trades)
                    recent_count = max(5, len(trades) // 3)
                    recent_trades = trades[-recent_count:]
                    recent_metrics = self.calculate_performance_metrics(recent_trades)
                    
                    print(f"\n📊 VALIDATION ({test_size//24} days, {len(trades)} trades):")
                    print(f"Overall: {overall_metrics['win_rate']:.1%} WR, {overall_metrics['profit_factor']:.2f} PF")
                    print(f"Recent ({recent_count}): {recent_metrics['win_rate']:.1%} WR, {recent_metrics['profit_factor']:.2f} PF")
                    
                    # Weighted decision: 70% recent + 30% overall
                    overall_ok = (
                        overall_metrics['win_rate'] >= self.min_win_rate and
                        overall_metrics['profit_factor'] >= self.min_profit_factor
                    )
                    
                    recent_ok = (
                        recent_metrics['win_rate'] >= (self.min_win_rate - 0.05) and  # 5% tolerance
                        recent_metrics['profit_factor'] >= (self.min_profit_factor - 0.2)  # 0.2 tolerance
                    )
                    
                    # Pass if: (Overall good AND Recent not terrible) OR (Recent good)
                    performance_ok = (overall_ok and recent_ok) or recent_metrics['win_rate'] >= self.min_win_rate
                    
                    status = "✅ PASSED" if performance_ok else "❌ FAILED"
                    print(f"Decision: {status}")
                    
                    return performance_ok, overall_metrics
            
            # If no period has enough trades, default to suspended
            print("⚠️ Insufficient historical trades for validation - Suspending signals")
            return False, None
            
        except Exception as e:
            print(f"Historical validation failed: {e}")
            return False, None

if __name__ == "__main__":
    monitor = PerformanceMonitor()
    print(monitor.get_performance_report())
    def post_retrain_validation(self):
        """Validate model after retraining using historical data"""
        data = self.load_performance_history()
        
        # Record new model version
        model_version = {
            'timestamp': datetime.now().isoformat(),
            'version': self.get_current_model_version(),
            'reason': 'monthly_retrain'
        }
        data['model_versions'].append(model_version)
        
        # Test model on historical data first
        print("📊 Testing new model on historical data...")
        passes_validation, metrics = self.validate_new_model_on_historical_data()
        
        if passes_validation:
            data['signal_status'] = 'active'
            print("🟢 NEW MODEL VALIDATED - Signals activated")
            logging.info("New model passed historical validation - Signals activated")
        else:
            data['signal_status'] = 'suspended'
            print("🔴 NEW MODEL FAILED - Signals suspended")
            logging.warning("New model failed historical validation - Signals suspended")
        
        # Store validation results
        if metrics:
            data['performance_metrics'] = metrics
        
        self.save_performance_history(data)
        return data['signal_status']