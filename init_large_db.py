#!/usr/bin/env python3
"""
Initialize large-scale database for NQL Agent demonstration
This script will generate 400k+ records across multiple tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import DatabaseManager

def main():
    print("🚀 Initializing Large-Scale NQL Agent Database")
    print("=" * 60)
    print("This will generate:")
    print("  • 50,000 users")
    print("  • 10,000 products") 
    print("  • 100,000 orders")
    print("  • 200,000 order items")
    print("  • 50,000 reviews")
    print("  • 10 categories")
    print("=" * 60)
    
    response = input("This may take 10-15 minutes. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    try:
        db_manager = DatabaseManager()
        print("\n🗄️  Initializing database...")
        db_manager.initialize_sample_data()
        
        print("\n✅ Large-scale database initialization completed!")
        print("\n📊 Database Statistics:")
        schema = db_manager.get_schema()
        for table_name, table_info in schema.items():
            print(f"  • {table_name}: {table_info['row_count']:,} rows")
        
        total_records = sum(table_info['row_count'] for table_info in schema.values())
        print(f"\n🎯 Total Records: {total_records:,}")
        print("\n🌐 Your NQL Agent is ready with enterprise-scale data!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

