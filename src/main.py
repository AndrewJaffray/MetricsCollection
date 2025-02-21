import json
import logging
import time
from pathlib import Path
from system_monitor import SystemMonitor
from stock_monitor import StockMonitor
from data_processor import DataProcessor
from visualizer import Visualizer
from flask import Flask, request, jsonify
from auth import require_auth, generate_token
from remote_control import RemoteControl
from dotenv import load_dotenv
import os

# Add this near the top of the file, before any code that uses environment variables
load_dotenv()

def setup_logging(config):
    """Configure logging based on config settings."""
    # Create logs directory if it doesn't exist
    log_path = Path(config['logging']['file_path'])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=config['logging']['level'],
        format=config['logging']['format'],
        handlers=[
            logging.FileHandler(config['logging']['file_path']),
            logging.StreamHandler()
        ]
    )

def load_config():
    """Load configuration from JSON file."""
    config_path = Path('config/config.json')
    with open(config_path) as f:
        return json.load(f)

def main():
    # Load configuration
    config = load_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

    try:
        # Initialize components
        system_monitor = SystemMonitor()
        stock_monitor = StockMonitor(config['monitoring']['stocks']['symbols'])
        data_processor = DataProcessor()
        visualizer = Visualizer()
        remote_control = RemoteControl()

        # Start Flask server
        app = Flask(__name__)
        
        @app.route('/metrics')
      #  @require_auth
        def get_metrics():
            system_data = system_monitor.get_metrics()
            stock_data = stock_monitor.get_metrics()
            processed_data = data_processor.process(system_data, stock_data)
            return processed_data

        @app.route('/')
       # @require_auth
        def dashboard():
            return visualizer.get_dashboard()

        @app.route('/command', methods=['POST'])
      #  @require_auth
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