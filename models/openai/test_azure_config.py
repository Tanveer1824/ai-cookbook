#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI configuration.
Run this script to test your Azure OpenAI setup.
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def test_azure_config():
    """Test Azure OpenAI configuration and basic functionality."""
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        return False
    
    print("✅ All required environment variables are set")
    
    # Test client initialization
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        print("✅ Azure OpenAI client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Azure OpenAI client: {e}")
        return False
    
    # Test basic API call
    try:
        print("🔄 Testing basic API call...")
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "user", "content": "Say 'Hello from Azure OpenAI!' and nothing else."}
            ],
            max_tokens=50
        )
        
        content = response.choices[0].message.content
        print(f"✅ API call successful! Response: {content}")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False
    
    print("\n🎉 Azure OpenAI configuration test completed successfully!")
    return True

if __name__ == "__main__":
    print("🧪 Testing Azure OpenAI Configuration...")
    print("=" * 50)
    
    success = test_azure_config()
    
    if success:
        print("\n✅ Your Azure OpenAI setup is working correctly!")
        print("You can now run any of the updated examples in this project.")
    else:
        print("\n❌ Azure OpenAI configuration test failed.")
        print("Please check the error messages above and fix any issues.")
        print("\nRefer to AZURE_MIGRATION_README.md for setup instructions.")
