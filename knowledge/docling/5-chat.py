import streamlit as st
import lancedb
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re
from typing import Dict, List, Any

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client with deployment-friendly config
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Make database path configurable for deployment
DB_PATH = os.getenv("DB_PATH", "data/lancedb")

def azure_openai_embedding(texts):
    """Custom embedding function using Azure OpenAI"""
    if isinstance(texts, str):
        texts = [texts]
    
    try:
        response = client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
            input=texts
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Azure OpenAI embedding error: {e}")
        raise

# Initialize LanceDB connection
@st.cache_resource
def init_db():
    """Initialize database connection.

    Returns:
        LanceDB table object
    """
    db = lancedb.connect(DB_PATH)
    return db.open_table("docling")


def get_context(query: str, table, num_results: int = 5) -> str:
    """Search the database for relevant context.

    Args:
        query: User's question
        table: LanceDB table object
        num_results: Number of results to return

    Returns:
        str: Concatenated context from relevant chunks with source information
    """
    # Convert query to vector using Azure OpenAI
    query_vector = azure_openai_embedding(query)[0]
    
    # Search using vector similarity
    results = table.search(query=query_vector, query_type="vector").limit(num_results).to_pandas()
    contexts = []

    for _, row in results.iterrows():
        # Extract metadata
        filename = row["metadata"]["filename"]
        page_numbers = row["metadata"]["page_numbers"]
        title = row["metadata"]["title"]

        # Build source citation
        source_parts = []
        if filename:
            source_parts.append(filename)
        if page_numbers:
            source_parts.append(f"p. {', '.join(str(p) for p in page_numbers)}")

        source = f"\nSource: {' - '.join(source_parts)}"
        if title:
            source += f"\nTitle: {title}"

        contexts.append(f"{row['text']}{source}")

    return "\n\n".join(contexts)


def get_chat_response(messages, context: str) -> str:
    """Get streaming response from Azure OpenAI API.

    Args:
        messages: Chat history
        context: Retrieved context from database

    Returns:
        str: Model's response
    """
    system_prompt = f"""You are a helpful real estate analyst assistant that answers questions based on the KFH Real Estate Report 2025 Q1.
    Use only the information from the provided context to answer questions. If you're unsure or the context
    doesn't contain the relevant information, say so.
    
    RESPONSE STYLE: CONCISE & FOCUSED
    - Keep answers brief and to the point
    - Use bullet points for key data
    - Highlight important numbers with **bold**
    - Avoid lengthy explanations unless specifically requested
    - Focus on the most relevant information first
    
    DEFINITION RESPONSES:
    - For "what is", "definition", "what does mean" questions:
      * Provide clear, concise definitions
      * Use bullet points for key characteristics
      * Highlight specific requirements or criteria with **bold**
      * Include relevant examples if available
      * Keep to 3-5 key points maximum
    
    VISUALIZATION REQUESTS:
    - When users ask for charts, graphs, or visualizations:
      * Provide a brief summary of the data that will be visualized
      * Mention that a chart has been generated and displayed
      * Keep the text response concise since the chart shows the data
    
    Context from KFH Real Estate Report 2025 Q1:
    {context}
    
    Always provide accurate, data-driven insights based on the report content.
    Be concise and direct in your responses.
    """

    messages_with_context = [{"role": "system", "content": system_prompt}, *messages]

    # Create the streaming response with controlled length
    stream = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        messages=messages_with_context,
        temperature=0.7,
        max_tokens=300,  # Limit response length for concise answers
        stream=True,
    )

    # Use Streamlit's built-in streaming capability
    response = st.write_stream(stream)
    return response

def extract_data_for_visualization(text: str, user_request: str = "") -> Dict[str, Any]:
    """Extract structured data from text for visualization with user request context"""
    data = {
        'categories': [],
        'values': [],
        'labels': [],
        'chart_type': 'bar',
        'title': 'Real Estate Data Visualization'
    }
    
    user_request_lower = user_request.lower()
    
    # Check if user is asking for specific data types
    is_investment_housing = any(term in user_request_lower for term in ['investment housing', 'investment residential', 'investment property'])
    is_rental_values = any(term in user_request_lower for term in ['rental values', 'rental value', 'rent values', 'rent value'])
    is_specific_sector = any(term in user_request_lower for term in ['private housing', 'commercial', 'industrial', 'coastline'])
    
    # Enhanced patterns for real estate financial data - more specific to avoid duplicates
    patterns = [
        # Investment housing specific patterns (highest priority)
        r'Investment\s*Housing[:\s]*([\d,]+\.?\d*)',                        # Investment Housing: 25.12
        r'Investment\s*Residential[:\s]*([\d,]+\.?\d*)',                    # Investment Residential: 25.12
        r'Investment\s*Property[:\s]*([\d,]+\.?\d*)',                       # Investment Property: 25.12
        r'([^:]+?)\s*Investment[:\s]*([\d,]+\.?\d*)',                       # Q1 2025, Investment: 25.12
        r'Q(\d)\s*(\d{4})[,\s]*Investment[:\s]*([\d,]+\.?\d*)',            # Q1 2025, Investment: 25.12
        
        # Private housing patterns
        r'Private\s*Housing[:\s]*([\d,]+\.?\d*)',                           # Private Housing: 38.63
        r'Private\s*Residential[:\s]*([\d,]+\.?\d*)',                       # Private Residential: 38.63
        
        # Commercial patterns
        r'Commercial[:\s]*([\d,]+\.?\d*)',                                  # Commercial: 18.45
        
        # Coastline patterns
        r'Coastline[:\s]*([\d,]+\.?\d*)',                                   # Coastline: 12.80
        
        # Industrial patterns
        r'Industrial[:\s]*([\d,]+\.?\d*)',                                  # Industrial: 5.00
        
        # Time-based patterns for trends (only if user asks for trends)
        r'Q(\d)\s*(\d{4})[:\s]*([\d,]+\.?\d*)',                            # Q1 2025: 425.8
        r'(\d{4})\s*Q(\d)[:\s]*([\d,]+\.?\d*)',                            # 2025 Q1: 425.8
        
        # Standard patterns (lower priority)
        r'([^:=\n]+)[:=]\s*([\d,]+\.?\d*)',                                # Category: Value
        r'([^=\n]+)=\s*([\d,]+\.?\d*)',                                     # Category = Value
        
        # Real estate specific patterns
        r'([^:]+?)\s*Credit\s*directed:\s*KD\s*([\d,]+\.?\d*)\s*billion',  # Credit directed: KD X.X billion
        r'([^:]+?)\s*Share:\s*([\d,]+\.?\d*)%',                             # Share: X.X%
        r'([^:]+?)\s*Total:\s*KD\s*([\d,]+\.?\d*)\s*billion',               # Total: KD X.X billion
        r'([^:]+?)\s*([\d,]+\.?\d*)\s*billion',                             # X.X billion
        r'([^:]+?)\s*([\d,]+\.?\d*)\s*million',                             # X.X million
        r'([^:]+?)\s*([\d,]+\.?\d*)%',                                      # X.X%
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) == 1:
                # Single value pattern (like Investment Housing: 25.12)
                category = "Investment Housing" if "Investment" in pattern else "Unknown"
                value_str = match[0].replace(',', '')
            elif len(match) == 2:
                # Two-value pattern (like Category: Value or Q1 2025, Investment: 25.12)
                category = match[0].strip()
                value_str = match[1].replace(',', '')
            elif len(match) == 3:
                # Time-based pattern (like Q1 2025: 425.8 or Q1 2025, Investment: 25.12)
                if 'Investment' in pattern:
                    category = f"Q{match[0]} {match[1]} Investment"
                    value_str = match[2].replace(',', '')
                elif 'Q' in pattern:
                    category = f"Q{match[0]} {match[1]}"
                    value_str = match[2].replace(',', '')
                else:
                    category = f"{match[0]} Q{match[1]}"
                    value_str = match[2].replace(',', '')
            else:
                continue
            
            try:
                value = float(value_str)
                if category and value > 0:
                    # Clean up category names
                    category = re.sub(r'\s+', ' ', category).strip()
                    category = re.sub(r'[^\w\s\-&]', '', category)  # Remove special chars except & and -
                    
                    # Skip if category is too generic or contains unwanted text
                    if (len(category) > 3 and 
                        not any(skip in category.lower() for skip in ['source:', 'page', 'file', 'pdf', 'report', 'title'])):
                        
                        # If user is asking for specific data, prioritize relevant matches
                        is_relevant = False
                        if is_investment_housing:
                            # For investment housing requests, only include investment-related data
                            if any(term in category.lower() for term in ['investment']):
                                is_relevant = True
                            # Include housing/residential data only if it's explicitly investment-related
                            elif any(term in category.lower() for term in ['housing', 'residential', 'property']) and 'investment' in category.lower():
                                is_relevant = True
                            # Include time-based data only if it's explicitly investment-related in the same context
                            elif any(term in category.lower() for term in ['q1', 'q2', 'q3', 'q4']) and ('investment' in category.lower() or 'investment' in text.lower()):
                                is_relevant = True
                        elif is_rental_values:
                            # For rental values requests, prioritize rental and time-based data
                            if any(term in category.lower() for term in ['rental', 'rent', 'value', 'price']):
                                is_relevant = True
                            elif any(term in category.lower() for term in ['q1', 'q2', 'q3', 'q4']):
                                is_relevant = True
                        elif is_specific_sector:
                            # For specific sector requests, only include that sector
                            if any(term in category.lower() for term in ['private', 'commercial', 'industrial', 'coastline']):
                                is_relevant = True
                        else:
                            is_relevant = True  # Include all data if no specific request
                        
                        if is_relevant:
                            # Avoid duplicates more strictly
                            if category not in data['categories'] and not any(cat in category for cat in data['categories']):
                                # Additional filtering for investment housing requests
                                if is_investment_housing:
                                    # Skip market segment data when asking for investment housing
                                    if any(term in category.lower() for term in ['private', 'commercial', 'industrial', 'coastline']):
                                        continue
                                
                                data['categories'].append(category)
                                data['values'].append(value)
                                data['labels'].append(f"{category}: {value:,.2f}")
            except ValueError:
                continue
    
    # If no data found, try to extract from common real estate terms
    if not data['values']:
        real_estate_keywords = [
            'real estate', 'construction', 'housing', 'credit', 'facilities', 
            'instalment', 'private', 'model', 'total', 'residential', 'commercial',
            'investment', 'development', 'market', 'price', 'value', 'rental'
        ]
        
        for keyword in real_estate_keywords:
            if keyword in text.lower():
                # Look for numbers near these keywords
                number_pattern = r'(\d+\.?\d*)'
                numbers = re.findall(number_pattern, text)
                if numbers:
                    try:
                        value = float(numbers[0])
                        if value > 0:
                            data['categories'].append(f"{keyword.title()}")
                            data['values'].append(value)
                            data['labels'].append(f"{keyword.title()}: {value:,.2f}")
                    except ValueError:
                        continue
    
    # Validate and clean the extracted data
    if data['values']:
        # Sort by values for better visualization
        sorted_data = sorted(zip(data['categories'], data['values']), key=lambda x: x[1], reverse=True)
        data['categories'] = [item[0] for item in sorted_data]
        data['values'] = [item[1] for item in sorted_data]
        
        # Limit to top 10 categories for readability
        if len(data['categories']) > 10:
            data['categories'] = data['categories'][:10]
            data['values'] = data['values'][:10]
    
    return data

def create_visualization(data: Dict[str, Any], chart_type: str = 'bar', user_request: str = "") -> go.Figure:
    """Create visualization based on data and chart type with user request context"""
    # Generate a more specific title based on user request
    if user_request:
        user_request_lower = user_request.lower()
        if 'investment housing' in user_request_lower:
            title = f"{chart_type.title()} Chart - Investment Housing Data"
        elif 'rental values' in user_request_lower or 'rental value' in user_request_lower:
            title = f"{chart_type.title()} Chart - Rental Values"
        elif 'private housing' in user_request_lower:
            title = f"{chart_type.title()} Chart - Private Housing Data"
        elif 'commercial' in user_request_lower:
            title = f"{chart_type.title()} Chart - Commercial Real Estate Data"
        elif 'trends' in user_request_lower or 'over time' in user_request_lower:
            title = f"{chart_type.title()} Chart - Trends Over Time"
        else:
            title = f"{chart_type.title()} Chart - Real Estate Data"
    else:
        title = f"{chart_type.title()} Chart - Real Estate Data"
    
    if chart_type == 'pie':
        fig = go.Figure(data=[
            go.Pie(
                labels=data['categories'],
                values=data['values'],
                textinfo='label+percent',
                insidetextorientation='radial'
            )
        ])
    elif chart_type == 'line':
        fig = go.Figure(data=[
            go.Scatter(
                x=data['categories'],
                y=data['values'],
                mode='lines+markers',
                line=dict(color='rgb(55, 83, 109)', width=3),
                marker=dict(size=8)
            )
        ])
    elif chart_type == 'scatter':
        fig = go.Figure(data=[
            go.Scatter(
                x=data['categories'],
                y=data['values'],
                mode='markers',
                marker=dict(
                    size=12,
                    color=data['values'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Value")
                )
            )
        ])
    elif chart_type == 'area':
        fig = go.Figure(data=[
            go.Scatter(
                x=data['categories'],
                y=data['values'],
                fill='tonexty',
                fillcolor='rgba(55, 83, 109, 0.3)',
                line=dict(color='rgb(55, 83, 109)', width=2)
            )
        ])
    else:  # Default to bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=data['categories'],
                y=data['values'],
                text=data['values'],
                texttemplate='%{text:,.0f}',
                textposition='outside',
                marker_color='rgb(55, 83, 109)'
            )
        ])
    
    # Ensure chart is readable
    if len(data['categories']) > 0:
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=400,
            xaxis_title="Categories",
            yaxis_title="Values",
            showlegend=False
        )
        
        # Rotate x-axis labels if there are many categories
        if len(data['categories']) > 5:
            fig.update_xaxes(tickangle=45)
    else:
        # Handle empty data case
        fig.update_layout(
            title="No Data Available for Visualization",
            template="plotly_white",
            height=400
        )
    
    return fig

def detect_visualization_request(user_input: str) -> bool:
    """Detect if user wants a visualization - improved detection for rental trends and charts"""
    user_input_lower = user_input.lower()
    
    # Enhanced visualization keywords including rental trends
    visualization_keywords = [
        # Explicit chart requests
        'create chart', 'make chart', 'show chart', 'display chart',
        'create graph', 'make graph', 'show graph', 'display graph',
        'create plot', 'make plot', 'show plot', 'display plot',
        'draw chart', 'draw graph', 'draw plot',
        'visualize', 'visualise', 'visualization', 'visualisation',
        'chart of', 'graph of', 'plot of',
        
        # Chart types
        'bar chart', 'pie chart', 'line chart', 'scatter plot',
        'heatmap', 'histogram', 'area chart',
        
        # Rental and trend specific requests
        'rental value trends', 'rental trends over time', 'rental value chart',
        'price trends', 'value trends', 'market trends chart',
        'trends over time', 'time series', 'quarterly trends',
        'line chart of', 'trend chart of', 'trend graph of',
        
        # Specific visualization requests
        'show me a chart', 'give me a chart', 'i want to see a chart',
        'can you create a chart', 'make a visualization'
    ]
    
    # Check for visualization keywords
    has_visualization_keyword = any(keyword in user_input_lower for keyword in visualization_keywords)
    
    # Check for time-related terms that suggest trends
    time_terms = ['over time', 'trends', 'quarterly', 'monthly', 'yearly', 'timeline', 'progression']
    has_time_terms = any(term in user_input_lower for term in time_terms)
    
    # Check for rental/value specific terms
    rental_terms = ['rental', 'rent', 'value', 'price', 'cost', 'market']
    has_rental_terms = any(term in user_input_lower for term in rental_terms)
    
    # Check for question words that suggest text-only responses
    question_words = ['what', 'how', 'why', 'when', 'where', 'summarize', 'explain', 'describe', 'tell me about']
    has_question_words = any(word in user_input_lower for word in question_words)
    
    # Return True if user explicitly wants visualization OR if they're asking about trends over time
    # BUT NOT if they're asking general questions about trends
    if has_visualization_keyword:
        return True
    elif has_time_terms and has_rental_terms and not has_question_words:
        return True
    else:
        return False

def detect_chart_type(user_input: str) -> str:
    """Detect the preferred chart type from user input"""
    user_input_lower = user_input.lower()
    
    # Check for explicit chart type requests first (highest priority)
    if 'bar chart' in user_input_lower or 'bar graph' in user_input_lower:
        return 'bar'
    elif 'pie chart' in user_input_lower or 'pie graph' in user_input_lower:
        return 'pie'
    elif 'line chart' in user_input_lower or 'line graph' in user_input_lower:
        return 'line'
    elif 'scatter plot' in user_input_lower or 'scatter chart' in user_input_lower:
        return 'scatter'
    elif 'area chart' in user_input_lower or 'area graph' in user_input_lower:
        return 'area'
    
    # Check for trend-related terms that suggest line charts
    if any(word in user_input_lower for word in ['trend', 'over time', 'time series', 'quarterly', 'monthly', 'yearly']):
        return 'line'
    
    # Then check for individual keywords
    if any(word in user_input_lower for word in ['bar', 'column', 'vertical', 'horizontal']):
        return 'bar'
    elif any(word in user_input_lower for word in ['pie', 'circle', 'donut', 'sector']):
        return 'pie'
    elif any(word in user_input_lower for word in ['line']):
        return 'line'
    elif any(word in user_input_lower for word in ['scatter', 'point', 'correlation']):
        return 'scatter'
    elif any(word in user_input_lower for word in ['area', 'filled']):
        return 'area'
    
    # If no specific chart type mentioned, default to line chart for trends, bar for others
    if 'trend' in user_input_lower or 'over time' in user_input_lower:
        return 'line'
    else:
        return 'bar'

def detect_definition_request(user_input: str) -> bool:
    """Detect if user is asking for a definition or explanation"""
    user_input_lower = user_input.lower()
    
    definition_keywords = [
        'what is', 'what are', 'definition', 'define', 'what does mean',
        'what does this mean', 'explain', 'describe', 'tell me about',
        'meaning of', 'concept of', 'understanding'
    ]
    
    return any(keyword in user_input_lower for keyword in definition_keywords)

def format_definition_response(response_text: str) -> str:
    """Format definition responses for better presentation"""
    
    # If response already has bullet points, enhance them
    if '•' in response_text or '*' in response_text:
        # Clean up existing bullet points
        formatted = response_text.replace('•', '•').replace('*', '•')
        
        # Add definition header if not present
        if not response_text.startswith('##'):
            formatted = f"## 📖 Definition\n\n{formatted}"
        
        return formatted
    
    # If no bullet points, try to structure the response
    sentences = response_text.split('. ')
    if len(sentences) > 1:
        formatted = "## 📖 Definition\n\n"
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                formatted += f"• {sentence.strip()}\n"
        return formatted
    
    return response_text

def create_data_summary_table(data: Dict[str, Any], user_request: str = "") -> str:
    """Create a summary table for the visualized data with user request context"""
    if not data['values']:
        return "No data available for summary."
    
    total = sum(data['values'])
    avg = total / len(data['values'])
    max_val = max(data['values'])
    min_val = min(data['values'])
    
    # Generate context-specific header
    if user_request:
        user_request_lower = user_request.lower()
        if 'investment housing' in user_request_lower:
            header = "## 📊 Investment Housing Data Summary"
        elif 'rental values' in user_request_lower or 'rental value' in user_request_lower:
            header = "## 📊 Rental Values Data Summary"
        elif 'private housing' in user_request_lower:
            header = "## 📊 Private Housing Data Summary"
        elif 'commercial' in user_request_lower:
            header = "## 📊 Commercial Real Estate Data Summary"
        elif 'trends' in user_request_lower or 'over time' in user_request_lower:
            header = "## 📊 Trends Data Summary"
        else:
            header = "## 📊 Data Summary"
    else:
        header = "## 📊 Data Summary"
    
    summary = f"{header}\n\n"
    summary += f"**Total Value**: {total:,.2f}\n\n"
    summary += f"**Average**: {avg:,.2f}\n\n"
    summary += f"**Range**: {min_val:,.2f} - {max_val:,.2f}\n\n"
    
    # Determine appropriate column headers based on data type
    if any('Q' in cat for cat in data['categories']) or any('202' in cat for cat in data['categories']):
        # Time-based data
        summary += "| Time Period | Value | Percentage |\n"
        summary += "|-------------|-------|------------|\n"
    else:
        # Category-based data
        summary += "| Category | Value | Percentage |\n"
        summary += "|----------|-------|------------|\n"
    
    for category, value in zip(data['categories'], data['values']):
        percentage = (value / total * 100) if total > 0 else 0
        summary += f"| {category} | {value:,.2f} | {percentage:.1f}% |\n"
    
    return summary

# Initialize Streamlit app
st.title("Markaz - Interactive Finance Assistant")
st.markdown("Ask questions about financial data and get AI-powered insights!")

# Basic security check for production
if os.getenv("ENVIRONMENT") == "production":
    password = st.text_input("Enter access password", type="password")
    if password != os.getenv("ACCESS_PASSWORD", "default123"):
        st.error("Incorrect password. Please try again.")
        st.stop()

# Check if required environment variables are set
required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    st.info("Please set these variables in your deployment environment.")
    st.stop()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize database connection
table = init_db()

# Display chat messages
if st.session_state.messages:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about financial data or request a chart..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get relevant context
    with st.status("🔍 Searching real estate report...", expanded=False) as status:
        context = get_context(prompt, table)
        st.markdown(
            """
            <style>
            .search-result {
                margin: 10px 0;
                padding: 10px;
                border-radius: 4px;
                background-color: #f0f2f6;
            }
            .search-result summary {
                cursor: pointer;
                color: #0f52ba;
                font-weight: 500;
            }
            .search-result summary:hover {
                color: #1e90ff;
            }
            .metadata {
                font-size: 0.9em;
                color: #666;
                font-style: italic;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        st.write("📄 Found relevant sections from the report:")
        for chunk in context.split("\n\n"):
            # Split into text and metadata parts
            parts = chunk.split("\n")
            text = parts[0]
            metadata = {
                line.split(": ")[0]: line.split(": ")[1]
                for line in parts[1:]
                if ": " in line
            }

            source = metadata.get("Source", "Unknown source")
            title = metadata.get("Title", "KFH Real Estate Report 2025 Q1")

            st.markdown(
                f"""
                <div class="search-result">
                    <details>
                        <summary>{source}</summary>
                        <div class="metadata">Section: {title}</div>
                        <div style="margin-top: 8px;">{text}</div>
                    </details>
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Display assistant response
    with st.chat_message("assistant"):
        # Check if user wants visualization first
        is_visualization_request = detect_visualization_request(prompt)
        
        if is_visualization_request:
            # Extract data from context for visualization
            viz_data = extract_data_for_visualization(context, prompt)
            
            if viz_data['values']:
                # Detect preferred chart type
                chart_type = detect_chart_type(prompt)
                
                # Create and display visualization
                fig = create_visualization(viz_data, chart_type, prompt)
                st.plotly_chart(fig, use_container_width=True)
                
                # Create data summary table
                summary_table = create_data_summary_table(viz_data, prompt)
                st.markdown(summary_table)
                
                # Store response for chat history
                response = f"Generated {chart_type} chart with {len(viz_data['categories'])} data points. The chart shows {chart_type} visualization of the requested data with a summary table below."
            else:
                response = "No numerical data found in the context for visualization. Try asking about specific numbers, percentages, or values from the report."
                st.warning("⚠️ No numerical data found in the context for visualization")
                st.info("Try asking about specific numbers, percentages, or values from the report")
        else:
            # Get regular model response with streaming for non-visualization requests
            response = get_chat_response(st.session_state.messages, context)
            
            # Check if this is a definition request and format accordingly
            if detect_definition_request(prompt):
                response = format_definition_response(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with helpful information
with st.sidebar:
    st.header("📊 Report Overview")
    st.info("This assistant can help you with questions about:")
    st.markdown("""
    - Market trends and analysis
    - Property valuations
    - Investment opportunities
    - Regional market insights
    - Economic indicators
    - Future projections
    """)
    
    st.header("💡 Sample Questions")
    st.markdown("""
    - "What are the key market trends for 2025?"
    - "How are property prices performing?"
    - "What investment opportunities are highlighted?"
    - "What's the outlook for residential vs commercial?"
    """)
    
    st.header("🎯 Response Style")
    st.info("**Concise & Focused Answers:**")
    st.markdown("""
    - Brief, to-the-point responses
    - Key data in bullet points
    - Important numbers highlighted
    - No lengthy explanations
    """)
    
    st.header("📈 Visualization Features")
    st.info("Ask for charts and graphs using keywords like:")
    st.markdown("""
    - **"Create a bar chart of..."**
    - **"Show me a pie chart for..."**
    - **"Make a line graph of..."**
    - **"Display a scatter plot of..."**
    - **"Rental value trends over time"**
    - **"Price trends chart"**
    """)
    
    st.header("🎯 Example Visualization Queries")
    st.markdown("""
    - "Create a bar chart of governorate prices"
    - "Show me a pie chart of market segments"
    - "Make a line graph of quarterly trends"
    - "Display rental value trends over time"
    - "Show me a chart of market performance"
    """)
    
    st.header("📝 Text vs. Charts")
    st.info("**Text Responses** for:")
    st.markdown("""
    - "Summarize the trends..."
    - "What are the price trends..."
    - "Explain the market analysis..."
    - "Tell me about..."
    """)
    
    st.info("**Charts + Summary** for:")
    st.markdown("""
    - "Create a chart of..."
    - "Show me a graph..."
    - "Visualize the data..."
    - "Rental trends over time..."
    - "Price trends chart..."
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
