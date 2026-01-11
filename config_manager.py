#!/usr/bin/env python3
"""
Gold AI Configuration Manager
Displays current settings and allows easy adjustments
"""

from app_config import AppConfig

def main():
    print("=" * 60)
    print("           GOLD AI CONFIGURATION MANAGER")
    print("=" * 60)
    
    print(AppConfig.get_config_summary())
    
    print("\nCurrent Activity Levels:")
    print(f"- Data fetching: Every {AppConfig.DATA_CACHE_DURATION//60} minutes")
    print(f"- Signal generation: Every {AppConfig.SIGNAL_CHECK_INTERVAL//60} minutes") 
    print(f"- Frontend status checks: Every {AppConfig.STATUS_POLL_INTERVAL//1000} seconds")
    print(f"- Performance updates: Every {AppConfig.PERFORMANCE_POLL_INTERVAL//60000} minutes")
    
    print("\nTo reduce system activity:")
    print("1. Increase DATA_CACHE_DURATION (currently 5 min)")
    print("2. Increase SIGNAL_CHECK_INTERVAL (currently 30 min)")
    print("3. Increase STATUS_POLL_INTERVAL (currently 2 min)")
    print("4. Increase PERFORMANCE_POLL_INTERVAL (currently 10 min)")
    
    print("\nTo modify settings:")
    print("- Edit app_config.py")
    print("- Restart the application")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()