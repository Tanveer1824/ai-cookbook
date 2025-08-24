#!/usr/bin/env python3
"""
Database Test Script for DocLing

This script tests if the database is properly set up and accessible.
Run this after setting up the database to verify everything is working.

Usage:
    python test_database.py
"""

import os
import sys
import lancedb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test basic database connection."""
    print("🔍 Testing database connection...")
    
    try:
        db_path = os.getenv("DB_PATH", "data/lancedb")
        print(f"   Database path: {db_path}")
        
        # Check if directory exists
        if not os.path.exists(db_path):
            print(f"   ❌ Database directory does not exist: {db_path}")
            return False
        
        # Try to connect
        db = lancedb.connect(db_path)
        print("   ✅ Database connection successful")
        return db
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

def test_table_access(db):
    """Test if the docling table exists and is accessible."""
    print("\n📋 Testing table access...")
    
    try:
        # List available tables
        tables = db.table_names()
        print(f"   Available tables: {tables}")
        
        if "docling" not in tables:
            print("   ❌ Table 'docling' not found")
            return False
        
        # Try to open the table
        table = db.open_table("docling")
        print("   ✅ Table 'docling' opened successfully")
        
        # Check table info
        row_count = table.count_rows()
        print(f"   📊 Table contains {row_count} rows")
        
        # Check schema
        schema = table.schema
        print(f"   🏗️  Table schema: {schema}")
        
        return table
        
    except Exception as e:
        print(f"   ❌ Table access failed: {e}")
        return False

def test_sample_query(table):
    """Test a sample vector search query."""
    print("\n🔍 Testing sample query...")
    
    try:
        # Check if we have any data
        if table.count_rows() == 0:
            print("   ⚠️  Table is empty - no data to query")
            return False
        
        # Try to get a sample row
        sample = table.to_pandas().head(1)
        if sample.empty:
            print("   ❌ Could not retrieve sample data")
            return False
        
        print("   ✅ Sample data retrieved successfully")
        print(f"   📄 Sample text length: {len(sample.iloc[0]['text'])} characters")
        
        # Check if vector column exists and has data
        if 'vector' in sample.columns:
            vector = sample.iloc[0]['vector']
            if vector and len(vector) > 0:
                print(f"   🧮 Vector dimension: {len(vector)}")
            else:
                print("   ⚠️  Vector column exists but is empty")
        else:
            print("   ❌ Vector column not found")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Sample query failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 DocLing Database Test")
    print("=" * 40)
    
    # Test 1: Database connection
    db = test_database_connection()
    if not db:
        print("\n❌ Database test failed at connection stage")
        print("Please run the setup scripts first:")
        print("   python setup_database.py")
        return False
    
    # Test 2: Table access
    table = test_table_access(db)
    if not table:
        print("\n❌ Database test failed at table access stage")
        print("Please ensure the database was created properly:")
        print("   python 3-embedding.py")
        return False
    
    # Test 3: Sample query
    query_success = test_sample_query(table)
    
    # Summary
    print("\n" + "=" * 40)
    if query_success:
        print("🎉 All database tests passed!")
        print("The database is ready for use with the chat interface.")
        print("\nYou can now run:")
        print("   streamlit run 5-chat.py")
        return True
    else:
        print("⚠️  Database tests partially passed")
        print("The database exists but may have issues with data or queries.")
        print("Please check the warnings above and consider re-running:")
        print("   python 3-embedding.py")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
