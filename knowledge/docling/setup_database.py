#!/usr/bin/env python3
"""
Database Setup Script for DocLing Chat Interface

This script helps set up the database by running the necessary processing steps
in the correct order to create the 'docling' table that the chat interface needs.

Usage:
    python setup_database.py

The script will:
1. Check if the PDF file exists
2. Run extraction, chunking, and embedding scripts
3. Verify the database is properly created
4. Provide status updates throughout the process
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_file_exists(filename):
    """Check if a file exists in the current directory."""
    if os.path.exists(filename):
        print(f"✅ Found {filename}")
        return True
    else:
        print(f"❌ {filename} not found in current directory")
        return False

def run_script(script_name, description):
    """Run a Python script and return success status."""
    print(f"\n🔄 {description}...")
    print(f"   Running {script_name}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, 
                              cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"   ✅ {description} completed successfully")
            return True
        else:
            print(f"   ❌ {description} failed with error:")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to run {script_name}: {e}")
        return False

def check_database():
    """Check if the database table was created successfully."""
    print("\n🔍 Checking database status...")
    
    try:
        import lancedb
        db = lancedb.connect("data/lancedb")
        tables = db.table_names()
        
        if "docling" in tables:
            table = db.open_table("docling")
            row_count = table.count_rows()
            print(f"   ✅ Database table 'docling' created successfully")
            print(f"   📊 Table contains {row_count} rows")
            return True
        else:
            print(f"   ❌ Table 'docling' not found in database")
            print(f"   📋 Available tables: {tables}")
            return False
            
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 DocLing Database Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    current_dir = os.getcwd()
    print(f"📁 Working directory: {current_dir}")
    
    # Check if required files exist
    required_files = [
        "1-extraction.py",
        "2-chunking.py", 
        "3-embedding.py",
        "KFH_Real_Estate_Report_2025_Q1.pdf"
    ]
    
    print("\n📋 Checking required files...")
    missing_files = []
    for file in required_files:
        if not check_file_exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all required files are in the current directory.")
        return False
    
    # Run the processing scripts in order
    scripts_to_run = [
        ("1-extraction.py", "Document extraction"),
        ("2-chunking.py", "Text chunking"),
        ("3-embedding.py", "Embedding generation and database creation")
    ]
    
    for script, description in scripts_to_run:
        if not run_script(script, description):
            print(f"\n❌ Setup failed at: {description}")
            print("Please check the error messages above and try again.")
            return False
        
        # Small delay between scripts
        time.sleep(1)
    
    # Verify the database was created
    if check_database():
        print("\n🎉 Database setup completed successfully!")
        print("You can now run the chat interface with:")
        print("   streamlit run 5-chat.py")
        return True
    else:
        print("\n❌ Database setup verification failed")
        print("Please check the error messages above and try again.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
