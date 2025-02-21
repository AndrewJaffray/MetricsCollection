import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_path="monitoring.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    timestamp TEXT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    running_processes INTEGER,
                    thread_count INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_metrics (
                    timestamp TEXT,
                    symbol TEXT,
                    price REAL,
                    volume INTEGER,
                    market_cap INTEGER
                )
            """)

    def store_system_metrics(self, metrics):
        """Store system metrics in the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, running_processes, thread_count)
                VALUES (?, ?, ?, ?, ?)
            """, (
                metrics['timestamp'],
                metrics['cpu_percent'],
                metrics['memory_percent'],
                metrics['running_processes'],
                metrics['thread_count']
            ))

    def store_stock_metrics(self, metrics):
        """Store stock metrics in the database."""
        with sqlite3.connect(self.db_path) as conn:
            timestamp = metrics['timestamp']
            for symbol, data in metrics['stocks'].items():
                conn.execute("""
                    INSERT INTO stock_metrics 
                    (timestamp, symbol, price, volume, market_cap)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    symbol,
                    data['price'],
                    data['volume'],
                    data['market_cap']
                ))

    def get_system_metrics(self, limit=100):
        """Retrieve latest system metrics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM system_metrics 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()

    def get_stock_metrics(self, symbol, limit=100):
        """Retrieve latest stock metrics for a given symbol."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM stock_metrics 
                WHERE symbol = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (symbol, limit))
            return cursor.fetchall() 