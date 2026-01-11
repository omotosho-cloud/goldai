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

class DataProcessor:
    def __init__(self):
        self.symbol = "GC=F"
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        self.use_polygon = bool(self.polygon_api_key)
        
    def fetch_data(self, period="max"):
        """Fetch maximum available hourly Gold data"""
        # Try multiple gold symbols with maximum data range
        symbols = ["GC=F", "GOLD", "GLD"]
        
        # Try different periods in order of preference
        periods_to_try = ["max", "10y", "5y", "2y", "1y"]
        
        for symbol in symbols:
            for period_attempt in periods_to_try:
                try:
                    print(f"Trying symbol: {symbol} with period: {period_attempt}")
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=period_attempt, interval="1h")
                    
                    if len(data) > 1000:  # Ensure we have substantial data
                        print(f"Successfully fetched {len(data)} data points from {symbol}")
                        print(f"Date range: {data.index[0]} to {data.index[-1]}")
                        self.symbol = symbol
                        return data.dropna()
                        
                except Exception as e:
                    print(f"Failed to fetch {symbol} with {period_attempt}: {e}")
                    continue
        
        # Fallback to daily data with maximum range if hourly fails
        print("Hourly data failed, trying daily data with maximum range...")
        for symbol in symbols:
            for period_attempt in periods_to_try:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=period_attempt, interval="1d")
                    
                    if len(data) > 500:
                        print(f"Using daily data from {symbol} with {len(data)} points")
                        print(f"Date range: {data.index[0]} to {data.index[-1]}")
                        self.symbol = symbol
                        return data.dropna()
                        
                except Exception as e:
                    continue
                
        raise Exception("Could not fetch any gold data")
    
    def add_indicators(self, df):
        """Calculate technical indicators"""
        if len(df) < 200:  # Ensure minimum data for indicators
            print(f"Warning: Only {len(df)} data points available")
            
        # RSI(14)
        if len(df) >= 14:
            df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
        else:
            df['RSI'] = 50  # Neutral RSI
        
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
            df['ADX'] = 15  # Below threshold
        
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
        """Main processing pipeline with maximum data range"""
        print("Fetching maximum available Gold data...")
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