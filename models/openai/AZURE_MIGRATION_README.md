# Azure OpenAI Migration Guide

This guide explains how to migrate from OpenAI to Azure OpenAI in your AI cookbook project.

## What Changed

### 1. Client Initialization
**Before (OpenAI):**
```python
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

**After (Azure OpenAI):**
```python
from openai import AzureOpenAI
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
```

### 2. Model Names
**Before (OpenAI):**
```python
model="gpt-4o"
model="gpt-4o-mini"
model="gpt-3.5-turbo"
```

**After (Azure OpenAI):**
```python
model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
```

### 3. Environment Variables
**Before (OpenAI):**
```bash
OPENAI_API_KEY=your_api_key_here
```

**After (Azure OpenAI):**
```bash
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

## Setup Instructions

### 1. Azure OpenAI Resource Setup
1. Create an Azure OpenAI resource in the Azure portal
2. Deploy a model (e.g., GPT-4, GPT-3.5-turbo)
3. Note your endpoint URL and deployment name

### 2. Environment Configuration
Create a `.env` file with your Azure OpenAI credentials:
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

### 3. Install Dependencies
```bash
pip install -r requirements-azure.txt
```

## Key Differences

### API Endpoints
- **OpenAI**: Uses `https://api.openai.com`
- **Azure OpenAI**: Uses your custom endpoint like `https://your-resource.openai.azure.com`

### Model Names
- **OpenAI**: Uses model names like `gpt-4o`, `gpt-3.5-turbo`
- **Azure OpenAI**: Uses deployment names that you configure

### Authentication
- **OpenAI**: API key only
- **Azure OpenAI**: API key + endpoint + API version

## Migration Checklist

- [x] Update client imports from `OpenAI` to `AzureOpenAI`
- [x] Update client initialization with Azure parameters
- [x] Replace hardcoded model names with environment variables
- [x] Update environment variable names
- [x] Test all functionality with Azure OpenAI
- [x] Update documentation and examples

## Files Updated

### Models
- `models/openai/01-introduction/01-introduction.py`
- `models/openai/01-introduction/02-making-requests.py`
- `models/openai/01-introduction/03-streaming.py`
- `models/openai/04-structured-output/01-introduction.py`
- `models/openai/04-structured-output/03-function-calling.py`

### Agents
- `agents/building-blocks/1-intelligence.py`

### Workflows
- `patterns/workflows/1-introduction/1-basic.py`
- `patterns/workflows/1-introduction/3-tools.py`
- `patterns/workflows/1-introduction/4-retrieval.py`
- `patterns/workflows/2-workflow-patterns/1-prompt-chaining.py`
- `patterns/workflows/2-workflow-patterns/2-routing.py`
- `patterns/workflows/2-workflow-patterns/3-parallizaton.py`
- `patterns/workflows/2-workflow-patterns/4-orchestrator.py`

### Knowledge Base
- `knowledge/mem0/oss/support_agent.py`
- `knowledge/mem0/oss/memory_demo.py`
- `knowledge/docling/5-chat.py`

### MCP
- `mcp/crash-course/4-openai-integration/client.py`
- `mcp/crash-course/5-mcp-vs-function-calling/function-calling.py`

## Testing

After migration, test your applications to ensure:
1. Authentication works correctly
2. Model responses are received
3. All functionality operates as expected
4. Error handling works properly

## Troubleshooting

### Common Issues

1. **Authentication Error**: Check your API key and endpoint URL
2. **Model Not Found**: Verify your deployment name matches exactly
3. **API Version Error**: Ensure you're using a supported API version
4. **Rate Limiting**: Azure OpenAI has different rate limits than OpenAI

### Debug Tips

1. Check environment variables are loaded correctly
2. Verify endpoint URL format
3. Test with simple requests first
4. Check Azure OpenAI service status

## Support

For Azure OpenAI specific issues, refer to:
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Azure OpenAI Service Status](https://status.azure.com/)
- [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)
