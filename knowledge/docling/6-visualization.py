import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import re
from typing import Dict, List, Any, Optional
import json

class RealEstateVisualizer:
    """Visualization class for KFH Real Estate Report data"""
    
    def __init__(self):
        self.chart_types = {
            'bar': 'Bar Chart',
            'pie': 'Pie Chart', 
            'line': 'Line Graph',
            'scatter': 'Scatter Plot',
            'heatmap': 'Heatmap',
            'area': 'Area Chart',
            'box': 'Box Plot',
            'histogram': 'Histogram'
        }
    
    def extract_data_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured data from text for visualization"""
        data = {
            'categories': [],
            'values': [],
            'labels': [],
            'chart_type': 'bar',
            'title': 'Real Estate Data Visualization'
        }
        
        # Extract numbers and text patterns
        # Look for patterns like "Category: Value" or "Category = Value"
        patterns = [
            r'([^:=\n]+)[:=]\s*([\d,]+\.?\d*)',  # Category: Value
            r'([^=\n]+)=\s*([\d,]+\.?\d*)',      # Category = Value
            r'([^,\n]+),\s*([\d,]+\.?\d*)',      # Category, Value
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                category = match[0].strip()
                value_str = match[1].replace(',', '')
                
                try:
                    value = float(value_str)
                    if category and value > 0:
                        data['categories'].append(category)
                        data['values'].append(value)
                        data['labels'].append(f"{category}: {value:,.0f}")
                except ValueError:
                    continue
        
        return data
    
    def create_bar_chart(self, data: Dict[str, Any]) -> go.Figure:
        """Create a bar chart"""
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
        
        fig.update_layout(
            title=data['title'],
            xaxis_title="Categories",
            yaxis_title="Values",
            template="plotly_white",
            height=500
        )
        
        return fig
    
    def create_pie_chart(self, data: Dict[str, Any]) -> go.Figure:
        """Create a pie chart"""
        fig = go.Figure(data=[
            go.Pie(
                labels=data['categories'],
                values=data['values'],
                textinfo='label+percent',
                insidetextorientation='radial'
            )
        ])
        
        fig.update_layout(
            title=data['title'],
            height=500
        )
        
        return fig
    
    def create_line_graph(self, data: Dict[str, Any]) -> go.Figure:
        """Create a line graph"""
        fig = go.Figure(data=[
            go.Scatter(
                x=data['categories'],
                y=data['values'],
                mode='lines+markers',
                line=dict(color='rgb(55, 83, 109)', width=3),
                marker=dict(size=8)
            )
        ])
        
        fig.update_layout(
            title=data['title'],
            xaxis_title="Categories",
            yaxis_title="Values",
            template="plotly_white",
            height=500
        )
        
        return fig
    
    def create_scatter_plot(self, data: Dict[str, Any]) -> go.Figure:
        """Create a scatter plot"""
        fig = go.Figure(data=[
            go.Scatter(
                x=data['categories'],
                y=data['values'],
                mode='markers',
                marker=dict(
                    size=12,
                    color=data['values'],
                    colorscale='Viridis',
                    showscale=True
                ),
                text=data['labels'],
                hovertemplate='<b>%{text}</b><extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=data['title'],
            xaxis_title="Categories",
            yaxis_title="Values",
            template="plotly_white",
            height=500
        )
        
        return fig
    
    def create_heatmap(self, data: Dict[str, Any]) -> go.Figure:
        """Create a heatmap (requires 2D data)"""
        # For heatmap, we need to create a matrix
        # This is a simplified version - you might want to enhance this
        if len(data['values']) > 1:
            # Create a simple 2D matrix
            matrix_size = int(np.ceil(np.sqrt(len(data['values']))))
            matrix = np.zeros((matrix_size, matrix_size))
            
            for i, value in enumerate(data['values']):
                row = i // matrix_size
                col = i % matrix_size
                if row < matrix_size and col < matrix_size:
                    matrix[row, col] = value
            
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                colorscale='Viridis',
                text=matrix,
                texttemplate='%{text:,.0f}',
                textfont={"size": 10}
            ))
            
            fig.update_layout(
                title=data['title'],
                height=500
            )
            
            return fig
        else:
            # Fallback to bar chart if not enough data
            return self.create_bar_chart(data)
    
    def create_area_chart(self, data: Dict[str, Any]) -> go.Figure:
        """Create an area chart"""
        fig = go.Figure(data=[
            go.Scatter(
                x=data['categories'],
                y=data['values'],
                fill='tonexty',
                fillcolor='rgba(55, 83, 109, 0.3)',
                line=dict(color='rgb(55, 83, 109)', width=2)
            )
        ])
        
        fig.update_layout(
            title=data['title'],
            xaxis_title="Categories",
            yaxis_title="Values",
            template="plotly_white",
            height=500
        )
        
        return fig
    
    def create_box_plot(self, data: Dict[str, Any]) -> go.Figure:
        """Create a box plot"""
        fig = go.Figure(data=[
            go.Box(
                y=data['values'],
                name="Values Distribution",
                boxpoints='outliers'
            )
        ])
        
        fig.update_layout(
            title=data['title'],
            yaxis_title="Values",
            template="plotly_white",
            height=500
        )
        
        return fig
    
    def create_histogram(self, data: Dict[str, Any]) -> go.Figure:
        """Create a histogram"""
        fig = go.Figure(data=[
            go.Histogram(
                x=data['values'],
                nbinsx=min(10, len(data['values'])),
                marker_color='rgb(55, 83, 109)'
            )
        ])
        
        fig.update_layout(
            title=data['title'],
            xaxis_title="Values",
            yaxis_title="Frequency",
            template="plotly_white",
            height=500
        )
        
        return fig
    
    def detect_chart_type(self, user_input: str) -> str:
        """Detect the preferred chart type from user input"""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['bar', 'column', 'vertical']):
            return 'bar'
        elif any(word in user_input_lower for word in ['pie', 'circle', 'donut']):
            return 'pie'
        elif any(word in user_input_lower for word in ['line', 'trend', 'time']):
            return 'line'
        elif any(word in user_input_lower for word in ['scatter', 'point', 'correlation']):
            return 'scatter'
        elif any(word in user_input_lower for word in ['heatmap', 'matrix', 'correlation']):
            return 'heatmap'
        elif any(word in user_input_lower for word in ['area', 'filled']):
            return 'area'
        elif any(word in user_input_lower for word in ['box', 'distribution', 'quartile']):
            return 'box'
        elif any(word in user_input_lower for word in ['histogram', 'frequency', 'distribution']):
            return 'histogram'
        else:
            return 'bar'  # Default
    
    def generate_visualization(self, text_data: str, user_input: str = "") -> go.Figure:
        """Generate visualization based on text data and user input"""
        # Extract data from text
        data = self.extract_data_from_text(text_data)
        
        # Detect chart type from user input
        chart_type = self.detect_chart_type(user_input)
        data['chart_type'] = chart_type
        
        # Update title based on chart type
        data['title'] = f"{self.chart_types[chart_type]} - {data['title']}"
        
        # Generate appropriate chart
        if chart_type == 'bar':
            return self.create_bar_chart(data)
        elif chart_type == 'pie':
            return self.create_pie_chart(data)
        elif chart_type == 'line':
            return self.create_line_graph(data)
        elif chart_type == 'scatter':
            return self.create_scatter_plot(data)
        elif chart_type == 'heatmap':
            return self.create_heatmap(data)
        elif chart_type == 'area':
            return self.create_area_chart(data)
        elif chart_type == 'box':
            return self.create_box_plot(data)
        elif chart_type == 'histogram':
            return self.create_histogram(data)
        else:
            return self.create_bar_chart(data)
    
    def get_chart_suggestions(self, data: Dict[str, Any]) -> List[str]:
        """Get suggestions for chart types based on data"""
        suggestions = []
        
        if len(data['values']) > 0:
            if len(data['values']) <= 10:
                suggestions.append("Bar Chart - Good for comparing categories")
                suggestions.append("Pie Chart - Good for showing proportions")
            
            if len(data['values']) > 3:
                suggestions.append("Line Graph - Good for showing trends")
                suggestions.append("Scatter Plot - Good for correlation analysis")
            
            if len(data['values']) > 5:
                suggestions.append("Area Chart - Good for cumulative data")
                suggestions.append("Box Plot - Good for distribution analysis")
                suggestions.append("Histogram - Good for frequency distribution")
        
        return suggestions

def create_visualization_interface():
    """Create the Streamlit interface for visualization"""
    st.header("📊 Real Estate Data Visualization")
    st.markdown("Generate charts and graphs from the KFH Real Estate Report data")
    
    # Initialize visualizer
    visualizer = RealEstateVisualizer()
    
    # Sidebar for chart type selection
    st.sidebar.header("Chart Options")
    selected_chart = st.sidebar.selectbox(
        "Select Chart Type:",
        list(visualizer.chart_types.keys()),
        format_func=lambda x: visualizer.chart_types[x]
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Data Input")
        
        # Sample data input
        sample_data = st.text_area(
            "Enter or paste real estate data (e.g., 'Ahmadi: 1250, Hawally: 980, Capital: 2100'):",
            height=150,
            placeholder="Enter data in format: Category: Value, Category: Value..."
        )
        
        # Or upload a file
        uploaded_file = st.file_uploader(
            "Or upload a CSV/Excel file:",
            type=['csv', 'xlsx', 'xls']
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"File uploaded successfully! Shape: {df.shape}")
                st.dataframe(df.head())
                
                # Convert DataFrame to text format for visualization
                if len(df.columns) >= 2:
                    sample_data = ""
                    for _, row in df.iterrows():
                        sample_data += f"{row.iloc[0]}: {row.iloc[1]}, "
                    sample_data = sample_data.rstrip(", ")
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    with col2:
        st.subheader("Chart Type")
        st.info(f"Selected: {visualizer.chart_types[selected_chart]}")
        
        # Show chart suggestions
        if sample_data:
            data = visualizer.extract_data_from_text(sample_data)
            suggestions = visualizer.get_chart_suggestions(data)
            
            st.subheader("💡 Suggestions")
            for suggestion in suggestions[:3]:  # Show first 3 suggestions
                st.write(f"• {suggestion}")
    
    # Generate and display visualization
    if sample_data:
        st.subheader("📈 Generated Visualization")
        
        try:
            # Generate chart
            fig = visualizer.generate_visualization(sample_data, selected_chart)
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data summary
            data = visualizer.extract_data_from_text(sample_data)
            if data['values']:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Categories", len(data['categories']))
                
                with col2:
                    st.metric("Total Value", f"{sum(data['values']):,.0f}")
                
                with col3:
                    st.metric("Average Value", f"{np.mean(data['values']):,.0f}")
                
                # Data table
                st.subheader("📋 Data Summary")
                df_summary = pd.DataFrame({
                    'Category': data['categories'],
                    'Value': data['values'],
                    'Percentage': [f"{(v/sum(data['values'])*100):.1f}%" for v in data['values']]
                })
                st.dataframe(df_summary, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error generating visualization: {e}")
            st.info("Try adjusting the data format or chart type")
    
    # Add some sample data for testing
    st.subheader("🧪 Sample Data for Testing")
    sample_inputs = [
        "Ahmadi: 1250, Hawally: 980, Capital: 2100, Jahra: 750, Mubarak Al-Kabeer: 890",
        "Q1 2023: 372.7, Q2 2023: 385.2, Q3 2023: 398.1, Q4 2023: 410.5, Q1 2025: 425.8",
        "Private Housing: 38.63, Investment: 25.12, Commercial: 18.45, Coastline: 12.80, Industrial: 5.00"
    ]
    
    for i, sample in enumerate(sample_inputs):
        if st.button(f"Load Sample {i+1}", key=f"sample_{i}"):
            st.session_state.sample_data = sample
            st.rerun()

if __name__ == "__main__":
    create_visualization_interface()
