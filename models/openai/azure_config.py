"""
Azure OpenAI Configuration
This module provides configuration for Azure OpenAI services.
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

def get_azure_client():
    """
    Get an Azure OpenAI client instance.
    
    Returns:
        AzureOpenAI: Configured Azure OpenAI client
    """
    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
    if not AZURE_OPENAI_ENDPOINT:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
    if not AZURE_OPENAI_DEPLOYMENT_NAME:
        raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME environment variable is required")
    
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

def get_model_name():
    """
    Get the Azure OpenAI model name.
    
    Returns:
        str: The model name for Azure OpenAI
    """
    return AZURE_OPENAI_DEPLOYMENT_NAME
