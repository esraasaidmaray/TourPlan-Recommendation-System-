"""
view_db.py
----------
Simple script to view SQLite database contents
"""

import sqlite3
import pandas as pd
import sys

DB_PATH = "poi.db"

def view_database():
    """View database contents in a readable format."""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Get table names
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📊 Database Tables:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"    Rows: {count}")
            
            # Show sample data
            if count > 0:
                df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 3", conn)
                print(f"    Sample data:")
                print(df.to_string(index=False))
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def view_table(table_name: str, limit: int = 10):
    """View specific table contents."""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Check if table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        if not cursor.fetchone():
            print(f"Table '{table_name}' not found!")
            return
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"📋 Table: {table_name}")
        print("Columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        print()
        
        # Get data
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit}", conn)
        print(f"Data (first {limit} rows):")
        print(df.to_string(index=False))
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        print(f"\nTotal rows: {total}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        view_table(table_name, limit)
    else:
        view_database()

