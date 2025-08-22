# Markaz - Interactive Finance Assistant

An AI-powered real estate analysis tool that provides insights from the KFH Real Estate Report 2025 Q1.

## 🚀 Quick Deploy to Streamlit Cloud

### Step 1: Fork/Clone this Repository
```bash
git clone <your-repo-url>
cd ai-cookbook-main
```

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set the path to: `knowledge/docling/5-chat.py`
6. Click "Deploy!"

### Step 3: Configure Environment Variables
In Streamlit Cloud, add these secrets:

```toml
AZURE_OPENAI_API_KEY = "your-azure-openai-api-key"
AZURE_OPENAI_ENDPOINT = "your-azure-endpoint"
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_OPENAI_DEPLOYMENT_NAME = "your-deployment-name"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = "your-embedding-deployment-name"
DB_PATH = "data/lancedb"
ENVIRONMENT = "production"
ACCESS_PASSWORD = "your-secure-password"
```

## 🔧 Local Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set Environment Variables
Create a `.env` file:
```env
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your-embedding-deployment
```

### Run Locally
```bash
streamlit run knowledge/docling/5-chat.py
```

## 📊 Features

- **AI-Powered Analysis**: Get insights from real estate reports
- **Smart Context Retrieval**: Relevant information from your database
- **Interactive Visualizations**: Charts and graphs when requested
- **Concise Responses**: Focused, to-the-point answers
- **Secure Access**: Password protection for production

## 🌐 Making it Public

### Option 1: Streamlit Cloud (Recommended)
- Free hosting
- Automatic deployments
- Custom domains supported
- SSL certificates included

### Option 2: Heroku
```bash
# Create Procfile
echo "web: streamlit run knowledge/docling/5-chat.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### Option 3: Docker
```bash
docker build -t markaz-app .
docker run -p 8501:8501 markaz-app
```

## 🔒 Security Notes

- Set strong `ACCESS_PASSWORD` for production
- Keep API keys secure
- Enable XSRF protection
- Use HTTPS in production

## 📝 Usage Examples

- "What are the rental rates in Salmiya?"
- "Create a chart of property prices"
- "Summarize market trends for 2025"
- "Compare residential vs commercial rates"

## 🆘 Troubleshooting

### Common Issues:
1. **Missing Environment Variables**: Check all required variables are set
2. **Database Connection**: Ensure `DB_PATH` is accessible
3. **API Limits**: Check Azure OpenAI quota and limits
4. **Memory Issues**: Reduce `max_tokens` if needed

## 📞 Support

For deployment issues, check:
- Streamlit Cloud logs
- Environment variable configuration
- Database accessibility
- API key permissions
