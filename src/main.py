import json
import logging
import time
from pathlib import Path
from Monitoring.system_monitor import SystemMonitor
from Monitoring.stock_monitor import StockMonitor
from Processing.data_processor import DataProcessor
from Visualization.visualizer import Visualizer
from flask import Flask, request, jsonify, render_template
from API.auth import require_auth, generate_token
from API.remote_control import RemoteControl
from dotenv import load_dotenv
import os
from custom_logging.logger import LoggerSingleton
from config.config_loader import load_config
from Database.database import Database
import sqlite3

# Add this near the top of the file, before any code that uses environment variables
load_dotenv()

def main():
    
    # Load configuration
    config_path = Path('src/config/config.json')
    config = load_config(config_path)
    
    # Initialize logging singleton
    LoggerSingleton(config)
    logger = LoggerSingleton.get_logger(__name__)

    try:
        # Initialize components
        system_monitor = SystemMonitor()
        
        # Get absolute path for the database
        project_root = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(os.path.dirname(project_root), config['database']['path'])
        database = Database(db_path)  # Initialize the database with absolute path
        
        # Initialize components with the database instance
        stock_monitor = StockMonitor(config['monitoring']['stocks']['symbols'], database)
        data_processor = DataProcessor(database)
        visualizer = Visualizer()
        remote_control = RemoteControl()

        # Start Flask server
        app = Flask(__name__)
        
        @app.route('/metrics')
        # @require_auth
        def get_metrics():
            system_data = system_monitor.get_metrics()
            stock_data = stock_monitor.get_metrics()
            processed_data = data_processor.process(system_data, stock_data)
            
            # Store metrics in the database
            try:
                # Store system metrics
                database.store_system_metrics({
                    'timestamp': processed_data['system']['timestamp'],
                    'cpu_percent': processed_data['system']['cpu']['usage_percent'],
                    'memory_percent': processed_data['system']['memory']['percent'],
                    'disk_percent': processed_data['system']['disk']['percent'],
                    'running_processes': processed_data['system']['processes']['count'],
                    'thread_count': processed_data['system']['processes']['threads']
                })
                
                # Store stock metrics
                database.store_stock_metrics({
                    'timestamp': processed_data['stocks']['timestamp'],
                    'stocks': {symbol: {
                        'price': data['price'],
                        'volume': data['volume'],
                        'change': data.get('change', 0),
                        'change_percent': data.get('change_percent', 0),
                        'market_cap': data.get('market_cap', 0)
                    } for symbol, data in processed_data['stocks']['data'].items()}
                })
            except Exception as e:
                logger.error(f"Error storing metrics in database: {str(e)}")
            
            return processed_data

        @app.route('/')
        def index():
            symbols = config['monitoring']['stocks']['symbols']
            monitor = StockMonitor(symbols=symbols)
            metrics = monitor.get_metrics()
            return visualizer.get_dashboard(metrics)
            
        @app.route('/history')
        def history_dashboard():
            return visualizer.get_history_dashboard()

        @app.route('/api/history/system', methods=['GET'])
        def get_system_history():
            limit = request.args.get('limit', default=100, type=int)
            system_metrics = database.get_system_metrics(limit)
            return jsonify(system_metrics)

        @app.route('/api/history/stock/<symbol>', methods=['GET'])
        def get_stock_history(symbol):
            limit = request.args.get('limit', default=100, type=int)
            stock_metrics = database.get_stock_metrics(symbol, limit)
            return jsonify(stock_metrics)
            
        @app.route('/api/devices', methods=['GET'])
        def get_devices():
            """Get a list of all devices in the database."""
            with sqlite3.connect(database.db_path) as conn:
                cursor = conn.execute("""
                    SELECT device_id, device_name, device_type, created_at
                    FROM devices
                    ORDER BY device_name
                """)
                
                devices = []
                for row in cursor.fetchall():
                    devices.append({
                        'id': row[0],
                        'name': row[1],
                        'type': row[2],
                        'created_at': row[3]
                    })
                
                return jsonify(devices)
                
        @app.route('/api/metrics', methods=['GET'])
        def get_metrics_list():
            """Get a list of all metrics in the database."""
            with sqlite3.connect(database.db_path) as conn:
                cursor = conn.execute("""
                    SELECT metric_id, metric_name, metric_type, unit, created_at
                    FROM metrics
                    ORDER BY metric_name
                """)
                
                metrics = []
                for row in cursor.fetchall():
                    metrics.append({
                        'id': row[0],
                        'name': row[1],
                        'type': row[2],
                        'unit': row[3],
                        'created_at': row[4]
                    })
                
                return jsonify(metrics)
                
        @app.route('/api/device/<device_name>/metric/<metric_name>/history', methods=['GET'])
        def get_metric_history(device_name, metric_name):
            """Get historical data for a specific device and metric."""
            start_time = request.args.get('start_time')
            end_time = request.args.get('end_time')
            interval = request.args.get('interval', default='hour')
            
            if request.args.get('aggregate', default='false').lower() == 'true':
                # Get aggregated data
                data = database.get_metrics_aggregated(device_name, metric_name, interval, start_time, end_time)
                result = []
                for row in data:
                    result.append({
                        'time_bucket': row[0],
                        'avg_value': row[1],
                        'min_value': row[2],
                        'max_value': row[3],
                        'count': row[4]
                    })
            else:
                # Get raw data
                data = database.get_metrics_by_timerange(device_name, metric_name, start_time, end_time)
                result = []
                for row in data:
                    result.append({
                        'timestamp': row[0],
                        'value': row[1]
                    })
                
            return jsonify(result)

        @app.route('/command', methods=['POST'])
        # @require_auth
        def execute_command():
            data = request.get_json()
            command = data.get('command')
            params = data.get('params', {})
            try:
                result = remote_control.execute_command(command, params)
                return jsonify({'success': True, 'result': result})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400

        @app.route('/login', methods=['POST'])
        def login():
            # For testing purposes, we'll use a simple authentication
            # In production, you should validate against a database
            auth_data = request.get_json()
            if auth_data and auth_data.get('username') == 'admin' and auth_data.get('password') == 'admin':
                token = generate_token('admin')
                return jsonify({'token': token})
            return jsonify({'message': 'Invalid credentials'}), 401

        # Run the Flask app
        app.run(
            host=config['server']['host'],
            port=config['server']['port']
        )

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main()) 