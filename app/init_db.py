#!/usr/bin/env python3
"""
Database initialization script for NQL Agent
This script initializes the database with sample data
"""

import os
import sys
import time
from database import DatabaseManager

def wait_for_database(max_retries=30, delay=2):
    """Wait for database to be ready"""
    print("Waiting for database to be ready...")
    
    for attempt in range(max_retries):
        try:
            db_manager = DatabaseManager()
            db_manager.test_connection()
            print("✅ Database connection successful!")
            return True
        except Exception as e:
            print(f"⏳ Attempt {attempt + 1}/{max_retries}: Database not ready yet ({e})")
            if attempt < max_retries - 1:
                time.sleep(delay)
    
    print("❌ Failed to connect to database after maximum retries")
    return False

def initialize_database():
    """Initialize database with sample data"""
    try:
        print("🚀 Initializing NQL Agent database...")
        
        # Wait for database to be ready
        if not wait_for_database():
            sys.exit(1)
        
        # Initialize sample data
        db_manager = DatabaseManager()
        db_manager.initialize_sample_data()
        
        print("✅ Database initialization completed successfully!")
        print("📊 Sample data has been loaded:")
        print("   - Users: Customer information")
        print("   - Products: Product catalog")
        print("   - Orders: Order history")
        print("   - Categories: Product categories")
        
        # Display some stats
        schema = db_manager.get_schema()
        print("\n📈 Database Statistics:")
        for table_name, table_info in schema.items():
            print(f"   - {table_name}: {table_info['row_count']} rows")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    initialize_database()
