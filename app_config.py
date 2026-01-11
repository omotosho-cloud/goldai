# Gold AI App Configuration
# Manual refresh approach - no automatic polling

class AppConfig:
    # Data fetching settings
    DATA_CACHE_DURATION = 300  # 5 minutes - how long to cache market data
    PRICE_CACHE_DURATION = 60  # 1 minute - how long to cache current price
    
    # Signal generation settings
    SIGNAL_CHECK_INTERVAL = 3600  # 1 hour - actual strategy timing
    
    # Frontend approach: Manual refresh only
    # No automatic polling - users click refresh buttons when needed
    
    # Error handling
    ERROR_RETRY_DELAY = 300  # 5 minutes - wait time after errors
    
    # Trading settings
    CONFIDENCE_THRESHOLD = 0.70  # 70% minimum confidence for signals
    
    # System behavior
    AUTO_START_SYSTEM = True  # Automatically start signal generation on app launch
    
    @classmethod
    def get_config_summary(cls):
        """Get a summary of current configuration"""
        return f"""
Gold AI Configuration (Manual Refresh Mode):
- Data cache: {cls.DATA_CACHE_DURATION//60} minutes
- Price cache: {cls.PRICE_CACHE_DURATION} seconds  
- Signal generation: Every {cls.SIGNAL_CHECK_INTERVAL//60} minutes (hourly)
- Frontend updates: Manual refresh buttons + WebSocket
- No automatic polling (efficient for hourly strategy)
- Confidence threshold: {cls.CONFIDENCE_THRESHOLD:.0%}
- Auto-start: {cls.AUTO_START_SYSTEM}
        """