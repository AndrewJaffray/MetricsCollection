import sqlite3
import os
import sys

def view_database(db_path="monitoring.db"):
    """View the structure and contents of the database."""
    # Convert to absolute path if it's a relative path
    if not os.path.isabs(db_path):
        # Use the project root directory (parent of src)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, db_path)
        
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist.")
        return
    
    try:
        # Connect to the database with a timeout
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Database: {db_path}")
        print(f"Tables: {[table[0] for table in tables]}")
        print("\n" + "="*50 + "\n")
        
        # For each table, show structure and sample data
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            print(f"Row count: {row_count}")
            
            # Show sample data (up to 5 rows)
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                rows = cursor.fetchall()
                print("Sample data:")
                for row in rows:
                    print(f"  {row}")
            
            print("\n" + "="*50 + "\n")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Use command line argument for database path if provided
    db_path = sys.argv[1] if len(sys.argv) > 1 else "monitoring.db"
    view_database(db_path) 