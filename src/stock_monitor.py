import yfinance as yf
from datetime import datetime, timedelta

class StockMonitor:
    def __init__(self, symbols):
        self.symbols = symbols

    def get_metrics(self):
        """Get current stock metrics."""
        stock_data = {}
        
        for symbol in self.symbols:
            try:
                stock = yf.Ticker(symbol)
                # Get today's data
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                hist = stock.history(start=yesterday, end=today + timedelta(days=1))
                
                if not hist.empty:
                    latest = hist.iloc[-1]
                    stock_data[symbol] = {
                        'price': round(latest['Close'], 2),
                        'volume': int(latest['Volume']),
                        'change': round(latest['Close'] - hist.iloc[0]['Close'], 2),
                        'change_percent': round(((latest['Close'] - hist.iloc[0]['Close']) / hist.iloc[0]['Close']) * 100, 2)
                    }
                else:
                    stock_data[symbol] = {'error': 'No data available'}
            except Exception as e:
                stock_data[symbol] = {'error': str(e)}
        
        return {
            'timestamp': datetime.now().isoformat(),
            'data': stock_data
        } 