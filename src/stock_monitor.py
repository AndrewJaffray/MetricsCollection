import requests
from datetime import datetime, timedelta
import json
import os
import time  # Import the time module

# Get the absolute path to the config file
config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')

# Load API key from configuration file
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

class StockMonitor:
    def __init__(self, symbols):
        self.symbols = symbols
        self.api_key = config['alpha_vantage_api_key']

    def get_metrics(self):
        """Get current stock metrics using Alpha Vantage."""
        stock_data = {}
        base_url = "https://www.alphavantage.co/query"

        for symbol in self.symbols:
            try:
                params = {
                    "function": "TIME_SERIES_INTRADAY",
                    "symbol": symbol,
                    "interval": "1min",
                    "apikey": self.api_key
                }
                response = requests.get(base_url, params=params)
                data = response.json()

                # Log the API response for debugging
                print(f"API response for {symbol}: {data}")

                if "Time Series (1min)" in data:
                    latest_time = max(data["Time Series (1min)"].keys())
                    latest_data = data["Time Series (1min)"][latest_time]
                    stock_data[symbol] = {
                        'price': round(float(latest_data['4. close']), 2),
                        'volume': int(latest_data['5. volume']),
                        'change': None,  # Alpha Vantage does not provide change directly
                        'change_percent': None  # Alpha Vantage does not provide change percent directly
                    }
                else:
                    stock_data[symbol] = {'error': 'No data available or API limit reached'}
            except Exception as e:
                stock_data[symbol] = {'error': str(e)}

            # Add a delay between requests
            time.sleep(12)  # Sleep for 12 seconds

        return {
            'timestamp': datetime.now().isoformat(),
            'data': stock_data
        }