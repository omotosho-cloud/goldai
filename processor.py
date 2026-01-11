import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import ADXIndicator, EMAIndicator
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import AverageTrueRange, BollingerBands
from datetime import datetime, timezone, timedelta
import pytz
import requests
import os
from app_config import AppConfig

class DataProcessor:
    def __init__(self):
        self.symbol = "GC=F"
        # Try multiple environment variable names
        self.polygon_api_key = (
            os.getenv('POLYGON_API_KEY') or 
            os.getenv('NEXT_PUBLIC_POLYGON_API_KEY') or
            'jrwKMe8SjF37sVie8Pfy_PTNFDhIEeOw'  # Direct fallback
        )
        self.use_polygon = bool(self.polygon_api_key)
        
        # Add caching to reduce API calls
        self._cached_data = None
        self._cache_timestamp = None
        self._cache_duration = AppConfig.DATA_CACHE_DURATION
        
        # Current price caching
        self._cached_price = None
        self._price_cache_timestamp = None
        self._price_cache_duration = AppConfig.PRICE_CACHE_DURATION
        
    def fetch_polygon_data(self, days=365):
        """Fetch gold data from Polygon API"""
        if not self.polygon_api_key:
            raise Exception("POLYGON_API_KEY not found in environment variables")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Polygon uses different symbol for gold futures
        symbol = "X:XAUUSD"  # Gold spot price in USD
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/hour/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        
        params = {
            'adjusted': 'true',
            'sort': 'asc',
            'apikey': self.polygon_api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'results' not in data or not data['results']:
                raise Exception("No data returned from Polygon API")
            
            # Convert to DataFrame
            df_data = []
            for bar in data['results']:
                df_data.append({
                    'timestamp': pd.to_datetime(bar['t'], unit='ms'),
                    'Open': bar['o'],
                    'High': bar['h'], 
                    'Low': bar['l'],
                    'Close': bar['c'],
                    'Volume': bar['v']
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('timestamp', inplace=True)
            
            print(f"Polygon: Fetched {len(df)} data points")
            print(f"Date range: {df.index[0]} to {df.index[-1]}")
            
            return df.dropna()
            
        except Exception as e:
            print(f"Polygon API error: {e}")
            raise
        
    def fetch_data(self, period="max"):
        """Fetch gold data from Polygon API or Yahoo Finance fallback with caching"""
        # Check cache first
        now = datetime.now()
        if (self._cached_data is not None and 
            self._cache_timestamp is not None and 
            (now - self._cache_timestamp).total_seconds() < self._cache_duration):
            print(f"Using cached data (age: {(now - self._cache_timestamp).total_seconds():.0f}s)")
            return self._cached_data
        
        # Try Polygon first if API key available
        if self.use_polygon:
            try:
                days_map = {
                    "1mo": 30,
                    "3mo": 90, 
                    "6mo": 180,
                    "1y": 365,
                    "2y": 730,
                    "max": 1825  # 5 years max for Polygon
                }
                days = days_map.get(period, 365)
                data = self.fetch_polygon_data(days)
                # Cache the result
                self._cached_data = data
                self._cache_timestamp = now
                return data
            except Exception as e:
                print(f"Polygon failed: {e}")
                print("Falling back to Yahoo Finance...")
        
        # Yahoo Finance fallback
        symbols = ["GC=F", "GOLD", "GLD"]
        periods_to_try = ["max", "10y", "5y", "2y", "1y"]
        
        for symbol in symbols:
            for period_attempt in periods_to_try:
                try:
                    print(f"Trying symbol: {symbol} with period: {period_attempt}")
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=period_attempt, interval="1h")
                    
                    if len(data) > 1000:
                        print(f"Successfully fetched {len(data)} data points from {symbol}")
                        print(f"Date range: {data.index[0]} to {data.index[-1]}")
                        self.symbol = symbol
                        # Cache the result
                        self._cached_data = data.dropna()
                        self._cache_timestamp = now
                        return self._cached_data
                        
                except Exception as e:
                    print(f"Failed to fetch {symbol} with {period_attempt}: {e}")
                    continue
        
        # Fallback to daily data if hourly fails
        print("Hourly data failed, trying daily data...")
        for symbol in symbols:
            for period_attempt in periods_to_try:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=period_attempt, interval="1d")
                    
                    if len(data) > 500:
                        print(f"Using daily data from {symbol} with {len(data)} points")
                        print(f"Date range: {data.index[0]} to {data.index[-1]}")
                        self.symbol = symbol
                        # Cache the result
                        self._cached_data = data.dropna()
                        self._cache_timestamp = now
                        return self._cached_data
                        
                except Exception as e:
                    continue
                
        raise Exception("Could not fetch any gold data")
    
    def get_current_price(self):
        """Get current gold price with caching"""
        now = datetime.now()
        
        # Check price cache first
        if (self._cached_price is not None and 
            self._price_cache_timestamp is not None and 
            (now - self._price_cache_timestamp).total_seconds() < self._price_cache_duration):
            return self._cached_price
        
        # Try to get current price
        symbols = ["GC=F", "GOLD", "GLD"]
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                if 'regularMarketPrice' in info:
                    price = float(info['regularMarketPrice'])
                    self._cached_price = price
                    self._price_cache_timestamp = now
                    return price
                elif 'currentPrice' in info:
                    price = float(info['currentPrice'])
                    self._cached_price = price
                    self._price_cache_timestamp = now
                    return price
            except Exception as e:
                print(f"Could not fetch current price from {symbol}: {e}")
                continue
        
        # Fallback: use last close price from cached data
        if self._cached_data is not None and len(self._cached_data) > 0:
            price = float(self._cached_data['Close'].iloc[-1])
            self._cached_price = price
            self._price_cache_timestamp = now
            return price
        
        print("Could not fetch current price")
        return None
    
    def add_indicators(self, df):
        """Calculate technical indicators"""
        if len(df) < 200:
            print(f"Warning: Only {len(df)} data points available")
            
        # RSI(14)
        if len(df) >= 14:
            df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
        else:
            df['RSI'] = 50
        
        # MACD(12,26,9)
        if len(df) >= 26:
            macd = MACD(df['Close'], window_slow=26, window_fast=12, window_sign=9)
            df['MACD'] = macd.macd()
            df['MACD_Signal'] = macd.macd_signal()
            df['MACD_Hist'] = macd.macd_diff()
        else:
            df['MACD'] = df['MACD_Signal'] = df['MACD_Hist'] = 0
        
        # EMA(20) and EMA(200)
        if len(df) >= 20:
            df['EMA_20'] = EMAIndicator(df['Close'], window=20).ema_indicator()
        else:
            df['EMA_20'] = df['Close']
            
        if len(df) >= 200:
            df['EMA_200'] = EMAIndicator(df['Close'], window=200).ema_indicator()
        else:
            df['EMA_200'] = df['Close']
        
        # ATR(14)
        if len(df) >= 14:
            df['ATR'] = AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()
        else:
            df['ATR'] = (df['High'] - df['Low']).rolling(window=min(len(df), 5)).mean()
        
        # ADX(14)
        if len(df) >= 14:
            df['ADX'] = ADXIndicator(df['High'], df['Low'], df['Close'], window=14).adx()
        else:
            df['ADX'] = 15
        
        # Bollinger BandWidth
        if len(df) >= 20:
            bb = BollingerBands(df['Close'], window=20, window_dev=2)
            df['BB_Width'] = (bb.bollinger_hband() - bb.bollinger_lband()) / bb.bollinger_mavg()
        else:
            df['BB_Width'] = 0.1
        
        return df
    
    def add_session_flags(self, df):
        """Add trading session binary flags"""
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        
        # Convert to GMT
        df_gmt = df.copy()
        df_gmt.index = df_gmt.index.tz_convert('GMT')
        
        # London Session (08:00-16:00 GMT)
        df['London_Session'] = ((df_gmt.index.hour >= 8) & (df_gmt.index.hour < 16)).astype(int)
        
        # New York Session (13:00-21:00 GMT)
        df['NY_Session'] = ((df_gmt.index.hour >= 13) & (df_gmt.index.hour < 21)).astype(int)
        
        # London/NY Overlap (13:00-16:00 GMT)
        df['Overlap_Session'] = ((df_gmt.index.hour >= 13) & (df_gmt.index.hour < 16)).astype(int)
        
        return df
    
    def create_labels(self, df):
        """Create trading labels based on 4h price movement and ADX"""
        df = df.copy()
        
        # Calculate 4h forward returns
        df['Future_Return_4h'] = (df['Close'].shift(-4) / df['Close'] - 1) * 100
        
        # Initialize labels
        df['Label'] = 0  # Neutral
        
        # Buy signals: +1% in 4h AND ADX > 20
        buy_condition = (df['Future_Return_4h'] >= 1.0) & (df['ADX'] > 20)
        df.loc[buy_condition, 'Label'] = 1
        
        # Sell signals: -1% in 4h AND ADX > 20
        sell_condition = (df['Future_Return_4h'] <= -1.0) & (df['ADX'] > 20)
        df.loc[sell_condition, 'Label'] = 2
        
        # Neutral: ADX < 20 OR price within +/- 1% range
        neutral_condition = (df['ADX'] < 20) | ((df['Future_Return_4h'] > -1.0) & (df['Future_Return_4h'] < 1.0))
        df.loc[neutral_condition, 'Label'] = 0
        
        return df
    
    def get_features(self, df):
        """Get feature columns for ML"""
        feature_cols = [
            'RSI', 'MACD', 'MACD_Signal', 'MACD_Hist',
            'EMA_20', 'EMA_200', 'ATR', 'ADX', 'BB_Width',
            'London_Session', 'NY_Session', 'Overlap_Session'
        ]
        return feature_cols
    
    def process_data(self):
        """Main processing pipeline"""
        print("Fetching Gold data...")
        if self.use_polygon:
            print("Using Polygon API for real-time data")
        else:
            print("Using Yahoo Finance (set POLYGON_API_KEY for better data)")
            
        df = self.fetch_data(period="max")
        
        print("Adding indicators...")
        df = self.add_indicators(df)
        
        print("Adding session flags...")
        df = self.add_session_flags(df)
        
        print("Creating labels...")
        df = self.create_labels(df)
        
        # Remove rows with NaN values
        df = df.dropna()
        
        print(f"Processed {len(df)} data points")
        print(f"Final date range: {df.index[0]} to {df.index[-1]}")
        print(f"Total duration: {(df.index[-1] - df.index[0]).days} days")
        return df

if __name__ == "__main__":
    processor = DataProcessor()
    data = processor.process_data()
    print(f"\nLabel distribution:\n{data['Label'].value_counts()}")
    print(f"\nData summary:")
    print(f"Total samples: {len(data)}")
    print(f"Date range: {data.index[0]} to {data.index[-1]}")
    print(f"Duration: {(data.index[-1] - data.index[0]).days} days")
    print(f"Avg samples per day: {len(data) / max(1, (data.index[-1] - data.index[0]).days):.1f}")