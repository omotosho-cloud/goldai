"""
Gold AI Signal Generation App
Modern web interface for professional trading signals
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from signal_generator import SignalGenerator
from trade_tracker import TradeTracker
from performance_monitor import PerformanceMonitor
from integrated_goldai import IntegratedGoldAI

def clean_for_json(obj):
    """Convert numpy/pandas types to JSON-serializable Python types"""
    if obj is None:
        return None
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    else:
        return obj

app = Flask(__name__)
app.config['SECRET_KEY'] = 'goldai_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances - Initialize with error handling
try:
    signal_generator = SignalGenerator()
except Exception as e:
    print(f"Warning: SignalGenerator initialization failed: {e}")
    print("Using fallback signal generator...")
    try:
        from fallback_signal import FallbackSignalGenerator
        signal_generator = FallbackSignalGenerator()
    except Exception as e2:
        print(f"Fallback signal generator also failed: {e2}")
        signal_generator = None

try:
    trade_tracker = TradeTracker()
except Exception as e:
    print(f"Warning: TradeTracker initialization failed: {e}")
    trade_tracker = None

try:
    performance_monitor = PerformanceMonitor()
except Exception as e:
    print(f"Warning: PerformanceMonitor initialization failed: {e}")
    performance_monitor = None

try:
    integrated_system = IntegratedGoldAI()
except Exception as e:
    print(f"Warning: IntegratedGoldAI initialization failed: {e}")
    integrated_system = None

# App state
app_state = {
    'running': False,
    'last_signal': None,
    'active_trades': [],
    'performance_data': {},
    'system_status': 'stopped'
}

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current system status"""
    status_data = {
        'running': bool(app_state['running']),
        'system_status': str(app_state['system_status']),
        'last_signal': clean_for_json(app_state['last_signal']),
        'active_trades_count': int(len(app_state['active_trades'])) if app_state['active_trades'] else 0,
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(clean_for_json(status_data))

@app.route('/api/signal/current')
def get_current_signal():
    """Get current market signal"""
    try:
        if signal_generator is None:
            return jsonify({'success': False, 'error': 'Signal generator not available'})
        
        signal = signal_generator.generate_signal()
        if signal:
            clean_signal = clean_for_json(signal)
            app_state['last_signal'] = clean_signal
            return jsonify({'success': True, 'signal': clean_signal})
        return jsonify({'success': False, 'message': 'No signal generated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trades/active')
def get_active_trades():
    """Get active trades"""
    try:
        if trade_tracker is None:
            return jsonify({'success': True, 'trades': []})
        
        trades = trade_tracker.get_active_trades()
        app_state['active_trades'] = trades
        return jsonify({'success': True, 'trades': trades})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    try:
        if performance_monitor is None:
            return jsonify({
                'success': True,
                'report': 'Performance monitoring not available',
                'metrics': {'win_rate': 0, 'profit_factor': 0, 'total_trades': 0},
                'status': 'unavailable'
            })
        
        report = performance_monitor.get_performance_report()
        metrics = performance_monitor.load_performance_history()
        return jsonify({
            'success': True,
            'report': report,
            'metrics': metrics.get('performance_metrics', {}),
            'status': metrics.get('signal_status', 'unknown')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system/start', methods=['POST'])
def start_system():
    """Start the AI signal system"""
    if not app_state['running']:
        app_state['running'] = True
        app_state['system_status'] = 'starting'
        
        # Start system in background thread
        thread = threading.Thread(target=run_signal_system)
        thread.daemon = True
        thread.start()
        
        # Wait a moment for system to start
        time.sleep(0.5)
        
        return jsonify({'success': True, 'message': 'System started successfully'})
    return jsonify({'success': False, 'message': 'System already running'})

@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    """Stop the AI signal system"""
    app_state['running'] = False
    app_state['system_status'] = 'stopped'
    return jsonify({'success': True, 'message': 'System stopped'})

@app.route('/api/retrain', methods=['POST'])
def retrain_model():
    """Force model retraining"""
    try:
        from model_trainer import ModelTrainer
        trainer = ModelTrainer()
        trainer.train_model()
        return jsonify({'success': True, 'message': 'Model retrained successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def run_signal_system():
    """Background thread for signal generation"""
    if signal_generator is None or trade_tracker is None:
        print("Cannot start signal system: Required components not available")
        app_state['system_status'] = 'error'
        return
    
    app_state['system_status'] = 'running'
    last_signal_hour = None
    
    while app_state['running']:
        try:
            current_hour = datetime.now().hour
            
            # Check trades
            if trade_tracker:
                try:
                    if hasattr(trade_tracker, 'check_trade_outcomes'):
                        trade_tracker.check_trade_outcomes()
                    if hasattr(trade_tracker, 'check_time_based_exits'):
                        trade_tracker.check_time_based_exits()
                except Exception as e:
                    print(f"Error checking trades: {e}")
            
            # Generate signal
            signal = signal_generator.generate_signal()
            
            if signal and signal['signal'] != 0 and current_hour != last_signal_hour:
                clean_signal = clean_for_json(signal)
                app_state['last_signal'] = clean_signal
                if trade_tracker and hasattr(trade_tracker, 'add_trade'):
                    try:
                        trade_tracker.add_trade(signal)
                    except Exception as e:
                        print(f"Error adding trade: {e}")
                last_signal_hour = current_hour
                
                # Emit to connected clients
                try:
                    socketio.emit('new_signal', clean_signal)
                except Exception as e:
                    print(f"Error emitting new signal: {e}")
                
            # Update active trades
            if trade_tracker:
                try:
                    active_trades = trade_tracker.get_active_trades() if hasattr(trade_tracker, 'get_active_trades') else []
                    app_state['active_trades'] = active_trades
                except Exception as e:
                    print(f"Error getting active trades: {e}")
                    app_state['active_trades'] = []
            
            # Emit status update
            try:
                socketio.emit('status_update', clean_for_json({
                    'timestamp': datetime.now().isoformat(),
                    'active_trades': int(len(app_state['active_trades'])),
                    'last_signal': app_state['last_signal']
                }))
            except Exception as e:
                print(f"Error emitting status update: {e}")
            
            time.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            print(f"Error in signal system: {e}")
            time.sleep(60)
    
    app_state['system_status'] = 'stopped'

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        emit('status_update', clean_for_json({
            'running': bool(app_state['running']),
            'system_status': str(app_state['system_status']),
            'last_signal': app_state['last_signal']
        }))
    except Exception as e:
        print(f"Error in socket connection: {e}")

if __name__ == '__main__':
    # Ensure model exists
    if not os.path.exists('gold_v1.joblib'):
        print("Training initial model...")
        from model_trainer import ModelTrainer
        trainer = ModelTrainer()
        trainer.train_model()
    
    print("🚀 Starting Gold AI Signal App")
    print("📊 Dashboard: http://localhost:5000")
    
    # Get port from environment (Railway sets PORT)
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    socketio.run(app, host=host, port=port, debug=False)