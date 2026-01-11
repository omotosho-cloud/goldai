from flask import Flask, render_template, jsonify, request
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')

# Import your modules
try:
    from signal_generator import SignalGenerator
    from trade_tracker import TradeTracker
    from performance_monitor import PerformanceMonitor
except ImportError:
    # Fallback for missing modules
    SignalGenerator = None
    TradeTracker = None
    PerformanceMonitor = None

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current system status"""
    return jsonify({
        'running': False,  # Serverless doesn't maintain state
        'system_status': 'serverless',
        'last_signal': None,
        'active_trades_count': 0,
        'timestamp': '2024-01-01T00:00:00'
    })

@app.route('/api/signal/current')
def get_current_signal():
    """Get current market signal"""
    try:
        if SignalGenerator:
            generator = SignalGenerator()
            signal = generator.generate_signal()
            if signal:
                return jsonify({'success': True, 'signal': signal})
        return jsonify({'success': False, 'message': 'Signal generation unavailable'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trades/active')
def get_active_trades():
    """Get active trades"""
    return jsonify({'success': True, 'trades': []})

@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    return jsonify({
        'success': True,
        'report': 'Performance monitoring unavailable in serverless mode',
        'metrics': {'win_rate': 0, 'profit_factor': 0, 'total_trades': 0},
        'status': 'serverless'
    })

@app.route('/api/system/start', methods=['POST'])
def start_system():
    """Start system (not applicable in serverless)"""
    return jsonify({'success': False, 'message': 'System control unavailable in serverless mode'})

@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    """Stop system (not applicable in serverless)"""
    return jsonify({'success': False, 'message': 'System control unavailable in serverless mode'})

@app.route('/api/retrain', methods=['POST'])
def retrain_model():
    """Retrain model (not applicable in serverless)"""
    return jsonify({'success': False, 'message': 'Model retraining unavailable in serverless mode'})

# Vercel handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)