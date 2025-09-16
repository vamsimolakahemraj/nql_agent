#!/usr/bin/env python3
"""
Test script for NQL Agent
This script tests various natural language queries
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_query(nql_query, expected_keywords=None):
    """Test a single NQL query"""
    print(f"\n🔍 Testing: '{nql_query}'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": nql_query},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("error"):
                print(f"❌ Error: {data['error']}")
                return False
            else:
                print(f"✅ SQL: {data['sql_query']}")
                print(f"📊 Results: {len(data['results'])} rows")
                print(f"⏱️  Time: {data['execution_time']:.3f}s")
                
                # Show first few results
                if data['results']:
                    print("📋 Sample results:")
                    for i, row in enumerate(data['results'][:3]):
                        print(f"   {i+1}. {row}")
                    if len(data['results']) > 3:
                        print(f"   ... and {len(data['results']) - 3} more")
                
                return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']}")
            print(f"🗄️  Database: {data['database']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_schema():
    """Test schema endpoint"""
    print("\n📋 Testing schema endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/schema", timeout=5)
        if response.status_code == 200:
            data = response.json()
            schema = data['schema']
            print(f"✅ Schema loaded: {len(schema)} tables")
            for table_name, table_info in schema.items():
                print(f"   - {table_name}: {table_info['row_count']} rows, {len(table_info['columns'])} columns")
            return True
        else:
            print(f"❌ Schema check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Schema check failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 NQL Agent Test Suite")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed. Make sure the application is running.")
        return
    
    # Test schema
    if not test_schema():
        print("\n❌ Schema check failed.")
        return
    
    # Test queries
    test_queries = [
        "Show all users",
        "Display all products",
        "Count all users",
        "Find users with age greater than 30",
        "Show products with price greater than 100",
        "Find users with email containing john",
        "What is the average price of products?",
        "Show completed orders",
        "Count products by category",
        "Find the most expensive product"
    ]
    
    print(f"\n🔍 Testing {len(test_queries)} queries...")
    print("=" * 50)
    
    passed = 0
    total = len(test_queries)
    
    for query in test_queries:
        if test_query(query):
            passed += 1
        time.sleep(0.5)  # Small delay between queries
    
    print(f"\n📊 Test Results: {passed}/{total} queries passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed")

if __name__ == "__main__":
    main()
