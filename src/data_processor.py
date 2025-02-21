import logging
import pandas as pd
from datetime import datetime
from database import Database

class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = Database()
        self.max_memory_size = 1000  # Keep last 1000 points in memory for quick access

    def process(self, system_data, stock_data):
        """Process and combine system and stock metrics."""
        return {
            'system': system_data,
            'stocks': stock_data,
            'summary': {
                'system_status': self._get_system_status(system_data),
                'stock_summary': self._get_stock_summary(stock_data)
            }
        }
    
    def _get_system_status(self, system_data):
        """Generate system status summary."""
        status = 'healthy'
        warnings = []
        
        # Check CPU usage
        if system_data['cpu']['usage_percent'] > 80:
            status = 'warning'
            warnings.append('High CPU usage')
            
        # Check memory usage
        if system_data['memory']['percent'] > 80:
            status = 'warning'
            warnings.append('High memory usage')
            
        # Check disk usage
        if system_data['disk']['percent'] > 80:
            status = 'warning'
            warnings.append('High disk usage')
            
        return {
            'status': status,
            'warnings': warnings
        }
    
    def _get_stock_summary(self, stock_data):
        """Generate stock summary."""
        summary = {
            'total_stocks': len(stock_data['data']),
            'stocks_up': 0,
            'stocks_down': 0
        }
        
        for symbol, data in stock_data['data'].items():
            if 'change' in data:
                if data['change'] > 0:
                    summary['stocks_up'] += 1
                elif data['change'] < 0:
                    summary['stocks_down'] += 1
                    
        return summary

    def get_historical_system_metrics(self):
        """Get historical system metrics from database."""
        metrics = self.db.get_system_metrics(self.max_memory_size)
        return {
            'timestamps': [m[0] for m in metrics],
            'cpu_percent': [m[1] for m in metrics],
            'memory_percent': [m[2] for m in metrics],
            'running_processes': [m[3] for m in metrics],
            'thread_count': [m[4] for m in metrics]
        }

    def get_historical_stock_metrics(self):
        """Get historical stock metrics from database."""
        processed_stocks = {}
        for symbol in ['GOOGL', 'AAPL']:  # Get from config in production
            metrics = self.db.get_stock_metrics(symbol, self.max_memory_size)
            processed_stocks[symbol] = {
                'timestamps': [m[0] for m in metrics],
                'prices': [m[2] for m in metrics],
                'volumes': [m[3] for m in metrics],
                'market_caps': [m[4] for m in metrics]
            }
        return processed_stocks 