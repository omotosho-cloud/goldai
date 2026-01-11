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
        this.startHourlyRefresh();
    }

    setupEventListeners() {
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
            console.log('New signal received via WebSocket:', signal);
            this.displaySignal(signal);
            this.showNotification(`New ${this.getSignalName(signal.signal)} signal generated!`, 'info');
            
            // Update last signal timestamp
            const now = new Date().toLocaleTimeString();
            console.log(`Signal updated at ${now}`);
        });

        this.socket.on('status_update', (data) => {
            console.log('Status update received:', data);
            this.updateStatus(data);
            // Auto-refresh status when system state changes
            this.refreshStatus();
        });
    }

    async loadInitialData() {
        console.log('Loading initial dashboard data...');
        await Promise.all([
            this.refreshStatus(),
            this.refreshCurrentSignal(),
            this.refreshActiveTrades(),
            this.refreshPerformance()
        ]);
        console.log('Initial data loaded successfully');
    }

    startHourlyRefresh() {
        // Sync to next hour and refresh hourly (aligned with signal generation)
        const now = new Date();
        const msToNextHour = (60 - now.getMinutes()) * 60 * 1000 - now.getSeconds() * 1000;
        
        console.log(`Next auto-refresh in ${Math.round(msToNextHour/60000)} minutes (at ${new Date(Date.now() + msToNextHour).toLocaleTimeString()})`);
        
        // First refresh at next hour
        setTimeout(() => {
            this.hourlyRefresh();
            // Then refresh every hour
            setInterval(() => {
                this.hourlyRefresh();
            }, 3600000); // 1 hour
        }, msToNextHour);
    }
    
    hourlyRefresh() {
        console.log('🔄 Hourly auto-refresh (aligned with signal generation)');
        this.refreshStatus();
        this.refreshActiveTrades();
        // Signal will come via WebSocket, but refresh in case of connection issues
        setTimeout(() => this.refreshCurrentSignal(), 2000);
    }





    async refreshStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            // System always running in production
            document.getElementById('system-status').textContent = 'Running';
            document.getElementById('active-trades-count').textContent = data.active_trades_count || 0;
            
            // Update status badge
            const badge = document.getElementById('status-badge');
            badge.textContent = 'Running';
            badge.className = 'badge bg-success me-2';
            
            console.log('Status updated: Production deployment');
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