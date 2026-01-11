"""
Auto Trading Module for Gold AI
Executes trades automatically via MetaTrader 5
"""

import MetaTrader5 as mt5
import logging
from datetime import datetime

class AutoTrader:
    def __init__(self, account=None, password=None, server=None):
        self.account = account
        self.password = password
        self.server = server
        self.symbol = "XAUUSD"
        self.lot_size = 0.01  # Start with micro lots
        self.max_risk_percent = 2.0  # Max 2% risk per trade
        
    def connect(self):
        """Connect to MetaTrader 5"""
        try:
            if not mt5.initialize():
                logging.error("MT5 initialization failed")
                return False
                
            if self.account:
                if not mt5.login(self.account, self.password, self.server):
                    logging.error("MT5 login failed")
                    return False
                    
            logging.info("MT5 connected successfully")
            return True
        except Exception as e:
            logging.error(f"MT5 connection error: {e}")
            return False
    
    def get_account_balance(self):
        """Get account balance"""
        try:
            account_info = mt5.account_info()
            return account_info.balance if account_info else 0
        except:
            return 0
    
    def calculate_lot_size(self, entry_price, sl_price):
        """Calculate position size based on risk management"""
        try:
            balance = self.get_account_balance()
            if balance <= 0:
                return self.lot_size
                
            risk_amount = balance * (self.max_risk_percent / 100)
            pip_value = abs(entry_price - sl_price)
            
            # Calculate lot size (simplified)
            calculated_lots = risk_amount / (pip_value * 100)
            
            # Limit to reasonable range
            return max(0.01, min(calculated_lots, 1.0))
        except:
            return self.lot_size
    
    def place_trade(self, signal):
        """Place trade based on signal"""
        if not self.connect():
            return False
            
        try:
            # Get current price
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                logging.error("Failed to get price data")
                return False
            
            # Determine trade type
            if signal['signal'] == 'BUY':
                trade_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
            elif signal['signal'] == 'SELL':
                trade_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
            else:
                return False
            
            # Calculate lot size
            lot_size = self.calculate_lot_size(price, signal['sl'])
            
            # Prepare trade request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": lot_size,
                "type": trade_type,
                "price": price,
                "sl": signal['sl'],
                "tp": signal['tp'],
                "deviation": 20,
                "magic": 12345,
                "comment": f"GoldAI_{signal['confidence']:.0f}%",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send trade
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"Trade failed: {result.retcode}")
                return False
            
            logging.info(f"Trade placed: {signal['signal']} {lot_size} lots at {price}")
            return True
            
        except Exception as e:
            logging.error(f"Trade execution error: {e}")
            return False
        finally:
            try:
                mt5.shutdown()
            except Exception as e:
                logging.error(f"MT5 shutdown error: {e}")
    
    def get_open_positions(self):
        """Get current open positions"""
        try:
            if not self.connect():
                return []
            positions = mt5.positions_get(symbol=self.symbol)
            return list(positions) if positions else []
        except Exception as e:
            logging.error(f"Get positions error: {e}")
            return []
        finally:
            try:
                mt5.shutdown()
            except Exception as e:
                logging.error(f"MT5 shutdown error: {e}")
    
    def close_all_positions(self):
        """Close all open positions"""
        try:
            if not self.connect():
                return False
                
            positions = self.get_open_positions()
            for position in positions:
                # Prepare close request
                if position.type == mt5.ORDER_TYPE_BUY:
                    trade_type = mt5.ORDER_TYPE_SELL
                    price = mt5.symbol_info_tick(self.symbol).bid
                else:
                    trade_type = mt5.ORDER_TYPE_BUY
                    price = mt5.symbol_info_tick(self.symbol).ask
                
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.symbol,
                    "volume": position.volume,
                    "type": trade_type,
                    "position": position.ticket,
                    "price": price,
                    "deviation": 20,
                    "magic": 12345,
                    "comment": "GoldAI_Close",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                mt5.order_send(request)
            
            return True
        except Exception as e:
            logging.error(f"Close positions error: {e}")
            return False
        finally:
            mt5.shutdown()

# Configuration template
AUTO_TRADE_CONFIG = {
    "enabled": False,  # Set to True to enable auto trading
    "account": None,   # Your MT5 account number
    "password": None,  # Your MT5 password
    "server": None,    # Your broker server
    "lot_size": 0.01,  # Position size
    "max_risk_percent": 2.0,  # Max risk per trade
}

if __name__ == "__main__":
    print("Auto Trading Setup:")
    print("1. Install MetaTrader 5")
    print("2. Install MT5 Python package: pip install MetaTrader5")
    print("3. Configure your broker details in AUTO_TRADE_CONFIG")
    print("4. Set enabled=True to activate auto trading")