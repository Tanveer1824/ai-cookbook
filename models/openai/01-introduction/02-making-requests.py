from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# The AzureOpenAI class will use the Azure environment variables
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
