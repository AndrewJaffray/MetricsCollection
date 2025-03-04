import sqlite3
from datetime import datetime, timedelta
import json
import os
import logging

class Database:
    """
    Database class for managing metrics collection and storage.
    Implements the DB component from the architecture diagram.
    """
    def __init__(self, db_path="monitoring.db"):
        # Convert to absolute path if it's a relative path
        if not os.path.isabs(db_path):
            # Use the project root directory (parent of src)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(project_root, db_path)
        else:
            self.db_path = db_path
            
        self.logger = logging.getLogger(__name__)
        self.timeout = 30.0  # Set a generous timeout for database operations
        self.init_database()

    def init_database(self):
        """Initialize the database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
            # Create devices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    device_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_name TEXT UNIQUE NOT NULL,
                    device_type TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT UNIQUE NOT NULL,
                    metric_type TEXT NOT NULL,
                    unit TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create device_metrics table (for storing actual metric values)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS device_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    metric_id INTEGER NOT NULL,
                    value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (device_id) REFERENCES devices (device_id),
                    FOREIGN KEY (metric_id) REFERENCES metrics (metric_id)
                )
            """)
            
            # Create indices for faster queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_device_metrics_device_id ON device_metrics(device_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_device_metrics_metric_id ON device_metrics(metric_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_device_metrics_timestamp ON device_metrics(timestamp)")
            
            # Insert default devices if they don't exist
            self._insert_default_data(conn)
            
            # Commit changes
            conn.commit()
    
    def _insert_default_data(self, conn):
        """Insert default devices and metrics if they don't exist."""
        # Default devices
        devices = [
            ("PC", "system"),
            ("Stock API", "external")
        ]
        
        for device_name, device_type in devices:
            conn.execute("""
                INSERT OR IGNORE INTO devices (device_name, device_type, created_at)
                VALUES (?, ?, ?)
            """, (device_name, device_type, datetime.now().isoformat()))
        
        # Default metrics for PC
        system_metrics = [
            ("CPU Usage", "percentage", "%"),
            ("Memory Usage", "percentage", "%"),
            ("Disk Usage", "percentage", "%"),
            ("Running Processes", "count", "processes"),
            ("Thread Count", "count", "threads")
        ]
        
        for metric_name, metric_type, unit in system_metrics:
            conn.execute("""
                INSERT OR IGNORE INTO metrics (metric_name, metric_type, unit, created_at)
                VALUES (?, ?, ?, ?)
            """, (metric_name, metric_type, unit, datetime.now().isoformat()))
        
        # Default metrics for stocks
        stock_metrics = [
            ("Price", "currency", "USD"),
            ("Volume", "count", "shares"),
            ("Change", "currency", "USD"),
            ("Change Percent", "percentage", "%"),
            ("Market Cap", "currency", "USD")
        ]
        
        for metric_name, metric_type, unit in stock_metrics:
            conn.execute("""
                INSERT OR IGNORE INTO metrics (metric_name, metric_type, unit, created_at)
                VALUES (?, ?, ?, ?)
            """, (metric_name, metric_type, unit, datetime.now().isoformat()))
    
    def get_device_id(self, device_name):
        """Get device ID by name, creating it if it doesn't exist."""
        with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
            cursor = conn.execute("""
                SELECT device_id FROM devices WHERE device_name = ?
            """, (device_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # Create a new device entry
                conn.execute("""
                    INSERT INTO devices (device_name, device_type, created_at)
                    VALUES (?, ?, ?)
                """, (device_name, "unknown", datetime.now().isoformat()))
                
                # Get the new device_id
                cursor = conn.execute("""
                    SELECT device_id FROM devices WHERE device_name = ?
                """, (device_name,))
                return cursor.fetchone()[0]
    
    def get_metric_id(self, metric_name):
        """Get metric ID by name, creating it if it doesn't exist."""
        with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
            cursor = conn.execute("""
                SELECT metric_id FROM metrics WHERE metric_name = ?
            """, (metric_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # Create a new metric entry
                conn.execute("""
                    INSERT INTO metrics (metric_name, metric_type, unit, created_at)
                    VALUES (?, ?, ?, ?)
                """, (metric_name, "unknown", "", datetime.now().isoformat()))
                
                # Get the new metric_id
                cursor = conn.execute("""
                    SELECT metric_id FROM metrics WHERE metric_name = ?
                """, (metric_name,))
                return cursor.fetchone()[0]
    
    def store_system_metrics(self, metrics):
        """Store system metrics in the database."""
        try:
            device_id = self.get_device_id("PC")
            timestamp = metrics.get('timestamp', datetime.now().isoformat())
            
            with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
                # Store CPU usage
                cpu_metric_id = self.get_metric_id("CPU Usage")
                conn.execute("""
                    INSERT INTO device_metrics (device_id, metric_id, value, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (device_id, cpu_metric_id, metrics.get('cpu_percent', 0), timestamp))
                
                # Store Memory usage
                memory_metric_id = self.get_metric_id("Memory Usage")
                conn.execute("""
                    INSERT INTO device_metrics (device_id, metric_id, value, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (device_id, memory_metric_id, metrics.get('memory_percent', 0), timestamp))
                
                # Store Disk usage if available
                if 'disk_percent' in metrics:
                    disk_metric_id = self.get_metric_id("Disk Usage")
                    conn.execute("""
                        INSERT INTO device_metrics (device_id, metric_id, value, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (device_id, disk_metric_id, metrics.get('disk_percent', 0), timestamp))
                
                # Store Running Processes
                processes_metric_id = self.get_metric_id("Running Processes")
                conn.execute("""
                    INSERT INTO device_metrics (device_id, metric_id, value, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (device_id, processes_metric_id, metrics.get('running_processes', 0), timestamp))
                
                # Store Thread Count
                threads_metric_id = self.get_metric_id("Thread Count")
                conn.execute("""
                    INSERT INTO device_metrics (device_id, metric_id, value, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (device_id, threads_metric_id, metrics.get('thread_count', 0), timestamp))
                
                # Commit the transaction
                conn.commit()
                
            self.logger.info(f"Stored system metrics at {timestamp}")
            return True
        except Exception as e:
            self.logger.error(f"Error storing system metrics: {str(e)}")
            return False

    def store_stock_metrics(self, metrics):
        """Store stock metrics in the database."""
        try:
            timestamp = metrics.get('timestamp', datetime.now().isoformat())
            
            with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
                for symbol, data in metrics.get('stocks', {}).items():
                    # Get or create device for this stock symbol
                    device_id = self.get_device_id(f"Stock-{symbol}")
                    
                    # Store Price
                    price_metric_id = self.get_metric_id("Price")
                    conn.execute("""
                        INSERT INTO device_metrics (device_id, metric_id, value, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (device_id, price_metric_id, data.get('price', 0), timestamp))
                    
                    # Store Volume
                    volume_metric_id = self.get_metric_id("Volume")
                    conn.execute("""
                        INSERT INTO device_metrics (device_id, metric_id, value, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (device_id, volume_metric_id, data.get('volume', 0), timestamp))
                    
                    # Store Change
                    change_metric_id = self.get_metric_id("Change")
                    conn.execute("""
                        INSERT INTO device_metrics (device_id, metric_id, value, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (device_id, change_metric_id, data.get('change', 0), timestamp))
                    
                    # Store Change Percent
                    change_percent_metric_id = self.get_metric_id("Change Percent")
                    conn.execute("""
                        INSERT INTO device_metrics (device_id, metric_id, value, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (device_id, change_percent_metric_id, data.get('change_percent', 0), timestamp))
                    
                    # Store Market Cap
                    market_cap_metric_id = self.get_metric_id("Market Cap")
                    conn.execute("""
                        INSERT INTO device_metrics (device_id, metric_id, value, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (device_id, market_cap_metric_id, data.get('market_cap', 0), timestamp))
                
                # Commit the transaction
                conn.commit()
            
            self.logger.info(f"Stored stock metrics at {timestamp}")
            return True
        except Exception as e:
            self.logger.error(f"Error storing stock metrics: {str(e)}")
            return False
    
    def get_system_metrics(self, limit=100):
        """Retrieve latest system metrics."""
        try:
            device_id = self.get_device_id("PC")
            
            with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
                # Get the latest timestamps
                cursor = conn.execute("""
                    SELECT DISTINCT timestamp 
                    FROM device_metrics 
                    WHERE device_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (device_id, limit))
                
                timestamps = [row[0] for row in cursor.fetchall()]
                
                result = []
                for timestamp in timestamps:
                    # Get all metrics for this timestamp
                    cursor = conn.execute("""
                        SELECT m.metric_name, dm.value
                        FROM device_metrics dm
                        JOIN metrics m ON dm.metric_id = m.metric_id
                        WHERE dm.device_id = ? AND dm.timestamp = ?
                    """, (device_id, timestamp))
                    
                    metrics = {}
                    for metric_name, value in cursor.fetchall():
                        metrics[metric_name.lower().replace(' ', '_')] = value
                    
                    metrics['timestamp'] = timestamp
                    result.append(metrics)
                
                return result
        except Exception as e:
            self.logger.error(f"Error retrieving system metrics: {str(e)}")
            return []
    
    def get_stock_metrics(self, symbol, limit=100):
        """Retrieve latest stock metrics for a given symbol."""
        try:
            device_id = self.get_device_id(f"Stock-{symbol}")
            
            with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
                # Get the latest timestamps
                cursor = conn.execute("""
                    SELECT DISTINCT timestamp 
                    FROM device_metrics 
                    WHERE device_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (device_id, limit))
                
                timestamps = [row[0] for row in cursor.fetchall()]
                
                result = []
                for timestamp in timestamps:
                    # Get all metrics for this timestamp
                    cursor = conn.execute("""
                        SELECT m.metric_name, dm.value
                        FROM device_metrics dm
                        JOIN metrics m ON dm.metric_id = m.metric_id
                        WHERE dm.device_id = ? AND dm.timestamp = ?
                    """, (device_id, timestamp))
                    
                    metrics = {}
                    for metric_name, value in cursor.fetchall():
                        metrics[metric_name.lower().replace(' ', '_')] = value
                    
                    metrics['timestamp'] = timestamp
                    metrics['symbol'] = symbol
                    result.append(metrics)
                
                return result
        except Exception as e:
            self.logger.error(f"Error retrieving stock metrics: {str(e)}")
            return []
    
    def get_available_stock_symbols(self):
        """Get a list of all stock symbols in the database."""
        try:
            with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
                cursor = conn.execute("""
                    SELECT device_name FROM devices
                    WHERE device_name LIKE 'Stock-%'
                    ORDER BY device_name
                """)
                
                # Extract symbol from device_name (remove 'Stock-' prefix)
                return [row[0].replace('Stock-', '') for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Error retrieving stock symbols: {str(e)}")
            return []
    
    def get_metrics_by_timerange(self, device_name, metric_name, start_time=None, end_time=None, limit=None):
        """Retrieve metrics within a specific time range."""
        if not start_time:
            # Default to last 24 hours
            start_time = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        if not end_time:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            device_id = self.get_device_id(device_name)
            metric_id = self.get_metric_id(metric_name)
            
            with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
                if limit:
                    cursor = conn.execute("""
                        SELECT timestamp, value
                        FROM device_metrics
                        WHERE device_id = ? AND metric_id = ? AND timestamp BETWEEN ? AND ?
                        ORDER BY timestamp ASC
                        LIMIT ?
                    """, (device_id, metric_id, start_time, end_time, limit))
                else:
                    cursor = conn.execute("""
                        SELECT timestamp, value
                        FROM device_metrics
                        WHERE device_id = ? AND metric_id = ? AND timestamp BETWEEN ? AND ?
                        ORDER BY timestamp ASC
                    """, (device_id, metric_id, start_time, end_time))
                
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Error retrieving metrics by timerange: {str(e)}")
            return []
    
    def get_metrics_aggregated(self, device_name, metric_name, interval='hour', start_time=None, end_time=None):
        """
        Retrieve aggregated metrics (avg, min, max) grouped by time interval.
        Interval can be 'hour', 'day', or 'week'.
        """
        if not start_time:
            # Default to last 7 days
            start_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        if not end_time:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Define the time format based on the interval
        if interval == 'hour':
            time_format = "%Y-%m-%d %H:00:00"
        elif interval == 'day':
            time_format = "%Y-%m-%d 00:00:00"
        elif interval == 'week':
            time_format = "%Y-%W" # Year and week number
        else:
            time_format = "%Y-%m-%d %H:00:00"  # Default to hourly
        
        try:
            device_id = self.get_device_id(device_name)
            metric_id = self.get_metric_id(metric_name)
            
            with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
                # Enable strftime function
                conn.create_function("strftime", 2, lambda fmt, timestamp: datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime(fmt))
                
                cursor = conn.execute(f"""
                    SELECT 
                        strftime(?, timestamp) as time_bucket,
                        AVG(value) as avg_value,
                        MIN(value) as min_value,
                        MAX(value) as max_value,
                        COUNT(*) as count
                    FROM device_metrics 
                    WHERE device_id = ? AND metric_id = ? AND timestamp BETWEEN ? AND ?
                    GROUP BY time_bucket
                    ORDER BY time_bucket ASC
                """, (time_format, device_id, metric_id, start_time, end_time))
                
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Error retrieving aggregated metrics: {str(e)}")
            return [] 