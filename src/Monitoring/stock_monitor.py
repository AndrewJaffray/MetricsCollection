import requests
from datetime import datetime, timedelta
import json
import os
import time  # Import the time module
import random  # Add import for random
from Database.database import Database

# Get the absolute path to the config file
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.json')

# Load API key from configuration file
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

class StockMonitor:
    def __init__(self, symbols, database=None):
        self.symbols = symbols
        self.api_key = config['alpha_vantage_api_key']
        self.db = database if database else Database()  # Use provided database or create new one
        self.previous_prices = {}  # Store previous prices
        self._load_previous_prices()  # Load previous prices from database

    def _load_previous_prices(self):
        """Load previous prices from the database for each symbol."""
        for symbol in self.symbols:
            try:
                # Get the most recent price from the database
                device_name = f"Stock-{symbol}"
                metric_name = "Price"
                data = self.db.get_metrics_by_timerange(device_name, metric_name, limit=1)
                
                if data and len(data) > 0:
                    # Value is at index 1 in the tuple
                    self.previous_prices[symbol] = data[0][1]
                else:
                    self.previous_prices[symbol] = None
            except Exception as e:
                print(f"Error loading previous price for {symbol}: {str(e)}")
                self.previous_prices[symbol] = None

    def get_metrics(self):
        """Get current stock metrics using mock data."""
        stock_data = {}
        
        # Use mock data for all symbols
        for symbol in self.symbols:
            try:
                # Generate mock data based on symbol with some randomness
                base_price = 150.0 + (hash(symbol) % 100)
                # Add random fluctuation of up to ±5%
                fluctuation = random.uniform(-0.05, 0.05)
                mock_price = base_price * (1 + fluctuation)
                mock_volume = 1000000 + (hash(symbol) % 9000000) + random.randint(-500000, 500000)
                
                # Calculate change based on previous price
                previous_price = self.previous_prices.get(symbol)
                if previous_price is not None:
                    change = mock_price - previous_price
                    change_percent = (change / previous_price) * 100 if previous_price > 0 else 0
                else:
                    change = 0
                    change_percent = 0
                
                # Store the current price for next time
                self.previous_prices[symbol] = mock_price
                
                # Create stock data entry
                stock_data[symbol] = {
                    'price': mock_price,
                    'volume': mock_volume,
                    'change': change,
                    'change_percent': change_percent,
                    'market_cap': mock_price * 1000000000  # Mock market cap
                }
                
                print(f"Using mock data for {symbol}: Price = ${mock_price:.2f}")
                
            except Exception as e:
                print(f"Error getting data for {symbol}: {str(e)}")
                # Provide fallback data
                stock_data[symbol] = {
                    'price': 0,
                    'volume': 0,
                    'change': 0,
                    'change_percent': 0,
                    'market_cap': 0
                }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'data': stock_data
        } 