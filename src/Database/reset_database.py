import os
import sqlite3
import time
import gc
from .database import Database

def reset_database(db_path="monitoring.db"):
    """Reset the database by deleting it and recreating it with the new schema."""
    # Convert to absolute path if it's a relative path
    if not os.path.isabs(db_path):
        # Use the project root directory (parent of src)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, db_path)
        
    print(f"Resetting database at {db_path}...")
    
    # Make sure any existing connections are closed
    # by forcing garbage collection
    gc.collect()
    
    # Delete the database file if it exists
    if os.path.exists(db_path):
        try:
            # Try to open and close the database to ensure it's not locked
            conn = sqlite3.connect(db_path, timeout=30.0)
            conn.close()
            
            # Wait a moment to ensure the connection is fully closed
            time.sleep(2)
            
            # Now try to delete the file
            os.remove(db_path)
            print(f"Deleted existing database file: {db_path}")
            
            # Wait after deletion
            time.sleep(2)
        except Exception as e:
            print(f"Error deleting database file: {str(e)}")
            return False
    
    # Create a new database with the schema
    try:
        # Wait before creating new database
        time.sleep(1)
        
        db = Database(db_path)
        print("Created new database with schema")
        
        # Wait before adding test data
        time.sleep(2)
        
        # Add some test data
        add_test_data(db)
        
        return True
    except Exception as e:
        print(f"Error creating new database: {str(e)}")
        return False

def add_test_data(db):
    """Add some test data to the database."""
    print("Adding test data...")
    
    # Add system metrics
    for i in range(10):
        hours_ago = 10 - i
        timestamp = f"2023-03-{4 - (hours_ago // 24)} {hours_ago % 24}:00:00"
        
        try:
            db.store_system_metrics({
                'timestamp': timestamp,
                'cpu_percent': 20 + (i * 5) % 30,  # Random-ish CPU usage between 20-50%
                'memory_percent': 30 + (i * 7) % 40,  # Random-ish memory usage between 30-70%
                'disk_percent': 45 + (i * 3) % 20,  # Random-ish disk usage between 45-65%
                'running_processes': 100 + (i * 11) % 50,  # Random-ish process count
                'thread_count': 1000 + (i * 123) % 500  # Random-ish thread count
            })
            # Add delay between operations
            time.sleep(1)
        except Exception as e:
            print(f"Error storing system metrics: {str(e)}")
            time.sleep(2)  # Wait longer if there's an error
    
    # Add stock metrics
    stocks = ['AAPL', 'GOOGL', 'MSFT']
    base_prices = {'AAPL': 150.0, 'GOOGL': 2500.0, 'MSFT': 300.0}
    
    for i in range(10):
        hours_ago = 10 - i
        timestamp = f"2023-03-{4 - (hours_ago // 24)} {hours_ago % 24}:00:00"
        
        stock_data = {}
        for symbol in stocks:
            base_price = base_prices[symbol]
            current_price = base_price + (i * 2) - 10  # Price trend
            
            stock_data[symbol] = {
                'price': current_price,
                'volume': 1000000 + (i * symbol.__hash__()) % 9000000,
                'change': 2.0 if i % 2 == 0 else -1.5,
                'change_percent': 1.2 if i % 2 == 0 else -0.8,
                'market_cap': current_price * 1000000000
            }
        
        try:
            # Add a longer delay between operations to avoid locks
            time.sleep(2)
            
            db.store_stock_metrics({
                'timestamp': timestamp,
                'stocks': stock_data
            })
        except Exception as e:
            print(f"Error storing stock metrics: {str(e)}")
            time.sleep(3)  # Wait even longer if there's an error
    
    print("Test data added successfully")

if __name__ == "__main__":
    success = reset_database()
    if success:
        print("Database reset completed successfully")
    else:
        print("Database reset failed") 