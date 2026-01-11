@echo off
echo ===============================================
echo           GOLD AI SYSTEM CONTROL
echo ===============================================
echo.

echo Current Configuration:
python config_manager.py
echo.

echo To stop the Gold AI app:
echo 1. Press Ctrl+C in the app terminal window
echo 2. Or close the terminal window
echo.

echo To reduce system activity, edit app_config.py:
echo - Increase DATA_CACHE_DURATION (data fetching frequency)
echo - Increase SIGNAL_CHECK_INTERVAL (signal generation frequency)  
echo - Increase STATUS_POLL_INTERVAL (frontend polling frequency)
echo.

echo The app has been optimized with:
echo - 5-minute data caching
echo - 30-minute signal generation
echo - 2-minute status polling
echo - 10-minute performance updates
echo.

pause