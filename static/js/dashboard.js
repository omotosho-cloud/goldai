// Gold AI Dashboard JavaScript

class GoldAIDashboard {
    constructor() {
        this.socket = io();
        this.isSystemRunning = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSocketListeners();
        this.loadInitialData();
        this.startPeriodicUpdates();
    }

    setupEventListeners() {
        // System toggle
        document.getElementById('toggle-system').addEventListener('click', () => {
            this.toggleSystem();
        });

        // Refresh buttons
        document.getElementById('refresh-signal').addEventListener('click', () => {
            this.refreshCurrentSignal();
        });

        document.getElementById('refresh-trades').addEventListener('click', () => {
            this.refreshActiveTrades();
        });

        document.getElementById('refresh-performance').addEventListener('click', () => {
            this.refreshPerformance();
        });

        // Retrain model
        document.getElementById('retrain-model').addEventListener('click', () => {
            this.retrainModel();
        });
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.showNotification('Connected to Gold AI system', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.showNotification('Disconnected from server', 'warning');
        });

        this.socket.on('new_signal', (signal) => {
            this.displaySignal(signal);
            this.showNotification(`New ${this.getSignalName(signal.signal)} signal generated!`, 'info');
        });

        this.socket.on('status_update', (data) => {
            this.updateStatus(data);
        });
    }

    async loadInitialData() {
        await Promise.all([
            this.refreshStatus(),
            this.refreshCurrentSignal(),
            this.refreshActiveTrades(),
            this.refreshPerformance()
        ]);
    }

    startPeriodicUpdates() {
        // Update status every 30 seconds
        setInterval(() => {
            this.refreshStatus();
        }, 30000);

        // Update performance every 5 minutes
        setInterval(() => {
            this.refreshPerformance();
        }, 300000);
    }

    async toggleSystem() {
        const button = document.getElementById('toggle-system');
        const originalText = button.textContent;
        
        button.disabled = true;
        button.innerHTML = '<span class="loading-spinner"></span> Processing...';

        try {
            const endpoint = this.isSystemRunning ? '/api/system/stop' : '/api/system/start';
            const response = await fetch(endpoint, { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.isSystemRunning = !this.isSystemRunning;
                this.updateSystemButton();
                this.showNotification(data.message, 'success');
            } else {
                this.showNotification(data.message || 'Operation failed', 'error');
            }
        } catch (error) {
            this.showNotification('Network error occurred', 'error');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }

    async refreshStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            this.isSystemRunning = data.running;
            this.updateSystemButton();
            this.updateStatusBadge(data.system_status);
            
            document.getElementById('system-status').textContent = 
                data.system_status.charAt(0).toUpperCase() + data.system_status.slice(1);
            document.getElementById('active-trades-count').textContent = data.active_trades_count;
        } catch (error) {
            console.error('Error refreshing status:', error);
        }
    }

    async refreshCurrentSignal() {
        const container = document.getElementById('current-signal');
        container.innerHTML = '<div class="text-center"><span class="loading-spinner"></span> Loading...</div>';

        try {
            const response = await fetch('/api/signal/current');
            const data = await response.json();

            if (data.success && data.signal) {
                this.displaySignal(data.signal);
            } else {
                container.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-chart-line fa-3x mb-3"></i>
                        <p>${data.message || 'No signal available'}</p>
                    </div>
                `;
            }
        } catch (error) {
            container.innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                    <p>Error loading signal</p>
                </div>
            `;
        }
    }

    async refreshActiveTrades() {
        const container = document.getElementById('active-trades');
        container.innerHTML = '<div class="text-center"><span class="loading-spinner"></span> Loading...</div>';

        try {
            const response = await fetch('/api/trades/active');
            const data = await response.json();

            if (data.success && data.trades && data.trades.length > 0) {
                this.displayActiveTrades(data.trades);
            } else {
                container.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-chart-bar fa-3x mb-3"></i>
                        <p>No active trades</p>
                    </div>
                `;
            }
        } catch (error) {
            container.innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                    <p>Error loading trades</p>
                </div>
            `;
        }
    }

    async refreshPerformance() {
        const container = document.getElementById('performance-report');
        container.innerHTML = '<div class="text-center"><span class="loading-spinner"></span> Loading...</div>';

        try {
            const response = await fetch('/api/performance');
            const data = await response.json();

            if (data.success) {
                this.displayPerformance(data);
                this.updatePerformanceCards(data.metrics);
            } else {
                container.innerHTML = `
                    <div class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                        <p>Error loading performance data</p>
                    </div>
                `;
            }
        } catch (error) {
            container.innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                    <p>Error loading performance data</p>
                </div>
            `;
        }
    }

    async retrainModel() {
        const button = document.getElementById('retrain-model');
        const originalText = button.textContent;
        
        button.disabled = true;
        button.innerHTML = '<span class="loading-spinner"></span> Retraining...';

        try {
            const response = await fetch('/api/retrain', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.showNotification('Model retrained successfully!', 'success');
            } else {
                this.showNotification(data.error || 'Retraining failed', 'error');
            }
        } catch (error) {
            this.showNotification('Network error during retraining', 'error');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }

    displaySignal(signal) {
        const container = document.getElementById('current-signal');
        const signalName = this.getSignalName(signal.signal);
        const signalClass = this.getSignalClass(signal.signal);
        const signalIcon = this.getSignalIcon(signal.signal);
        
        // Check if fallback mode
        const isFallback = signal.session && signal.session.includes('FALLBACK');
        const fallbackWarning = isFallback ? `
            <div class="alert alert-warning mb-3">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>FALLBACK MODE:</strong> ML model unavailable. Using basic technical analysis.
                <br><small>Signals may be less accurate. Use with extra caution!</small>
            </div>
        ` : '';

        container.innerHTML = `
            ${fallbackWarning}
            <div class="signal-card ${signalClass} p-3">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <span class="signal-badge badge bg-${signalClass === 'buy' ? 'success' : signalClass === 'sell' ? 'danger' : 'secondary'}">
                        ${signalIcon} ${signalName}
                    </span>
                    <small class="text-muted">${new Date(signal.timestamp).toLocaleString()}</small>
                </div>
                
                <div class="row">
                    <div class="col-6">
                        <div class="metric-item">
                            <div class="metric-label">Entry Price</div>
                            <div class="metric-value">$${signal.entry_price.toFixed(2)}</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="metric-item">
                            <div class="metric-label">Confidence</div>
                            <div class="metric-value">${(signal.confidence * 100).toFixed(1)}%</div>
                        </div>
                    </div>
                </div>

                ${signal.signal !== 0 ? `
                <div class="row mt-3">
                    <div class="col-6">
                        <div class="metric-item">
                            <div class="metric-label">Stop Loss</div>
                            <div class="metric-value text-danger">$${signal.stop_loss.toFixed(2)}</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="metric-item">
                            <div class="metric-label">Take Profit</div>
                            <div class="metric-value text-success">$${signal.take_profit.toFixed(2)}</div>
                        </div>
                    </div>
                </div>
                ` : ''}

                <div class="mt-3">
                    <div class="metric-label">Confidence Level</div>
                    <div class="confidence-bar mt-1">
                        <div class="confidence-indicator" style="width: ${signal.confidence * 100}%"></div>
                    </div>
                </div>

                <div class="row mt-3">
                    <div class="col-4">
                        <small class="text-muted">Session: ${signal.session}</small>
                    </div>
                    <div class="col-4">
                        <small class="text-muted">RSI: ${signal.rsi.toFixed(1)}</small>
                    </div>
                    <div class="col-4">
                        <small class="text-muted">ADX: ${signal.adx.toFixed(1)}</small>
                    </div>
                </div>
            </div>
        `;
    }

    displayActiveTrades(trades) {
        const container = document.getElementById('active-trades');
        
        container.innerHTML = trades.map(trade => `
            <div class="trade-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${this.getSignalName(trade.signal)} ${this.getSignalIcon(trade.signal)}</strong>
                        <br>
                        <small class="text-muted">Entry: $${trade.entry_price.toFixed(2)}</small>
                    </div>
                    <div class="text-end">
                        <div class="badge bg-${trade.signal === 1 ? 'success' : 'danger'}">
                            ${(trade.confidence * 100).toFixed(1)}%
                        </div>
                        <br>
                        <small class="text-muted">${new Date(trade.timestamp).toLocaleTimeString()}</small>
                    </div>
                </div>
            </div>
        `).join('');
    }

    displayPerformance(data) {
        const container = document.getElementById('performance-report');
        
        container.innerHTML = `
            <div class="performance-grid">
                <div class="performance-item">
                    <div class="metric-label">Signal Status</div>
                    <div class="metric-value">
                        <span class="status-indicator status-${data.status === 'active' ? 'running' : 'stopped'}"></span>
                        ${data.status.toUpperCase()}
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <pre class="bg-light p-3 rounded">${data.report}</pre>
            </div>
        `;
    }

    updatePerformanceCards(metrics) {
        if (metrics.win_rate !== undefined) {
            document.getElementById('win-rate').textContent = `${(metrics.win_rate * 100).toFixed(1)}%`;
        }
        if (metrics.profit_factor !== undefined) {
            document.getElementById('profit-factor').textContent = metrics.profit_factor.toFixed(2);
        }
    }

    updateSystemButton() {
        const button = document.getElementById('toggle-system');
        if (this.isSystemRunning) {
            button.textContent = 'Stop System';
            button.className = 'btn btn-danger btn-sm';
        } else {
            button.textContent = 'Start System';
            button.className = 'btn btn-success btn-sm btn-pulse';
        }
    }

    updateStatusBadge(status) {
        const badge = document.getElementById('status-badge');
        badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        
        badge.className = 'badge me-2 ';
        switch (status) {
            case 'running':
                badge.className += 'bg-success';
                break;
            case 'starting':
                badge.className += 'bg-warning';
                break;
            default:
                badge.className += 'bg-secondary';
        }
    }

    updateStatus(data) {
        if (data.active_trades !== undefined) {
            document.getElementById('active-trades-count').textContent = data.active_trades;
        }
    }

    getSignalName(signal) {
        const names = { 0: 'NEUTRAL', 1: 'BUY', 2: 'SELL' };
        return names[signal] || 'UNKNOWN';
    }

    getSignalClass(signal) {
        const classes = { 0: 'neutral', 1: 'buy', 2: 'sell' };
        return classes[signal] || 'neutral';
    }

    getSignalIcon(signal) {
        const icons = { 0: '⚪', 1: '🟢', 2: '🔴' };
        return icons[signal] || '⚪';
    }

    showNotification(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        const toastBody = toast.querySelector('.toast-body');
        
        toastBody.textContent = message;
        
        // Update toast styling based on type
        toast.className = `toast border-${type === 'error' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'info'}`;
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GoldAIDashboard();
});