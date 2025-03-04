import os
import sqlite3
import sys

def check_database(db_path="monitoring.db"):
    """Check if the database file exists and is accessible."""
    # Convert to absolute path if it's a relative path
    if not os.path.isabs(db_path):
        # Use the project root directory (parent of src)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, db_path)
        
    print(f"Checking database at {db_path}...")
    
    # Check if file exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist.")
        return False
    
    print(f"Database file {db_path} exists.")
    print(f"File size: {os.path.getsize(db_path)} bytes")
    
    # Try to connect to the database
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        cursor = conn.cursor()
        
        # Check if we can execute a simple query
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        print(f"Successfully connected to database. SQLite version: {version[0]}")
        
        # Check if the database has tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if tables:
            print(f"Database contains {len(tables)} tables: {[table[0] for table in tables]}")
        else:
            print("Database does not contain any tables.")
        
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Use command line argument for database path if provided
    db_path = sys.argv[1] if len(sys.argv) > 1 else "monitoring.db"
    check_database(db_path) 