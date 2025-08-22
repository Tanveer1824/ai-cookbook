#!/usr/bin/env python3
"""
Demo script showcasing the visualization capabilities of the Real Estate Visualizer
"""

import streamlit as st
import pandas as pd
import numpy as np
from 6_visualization import RealEstateVisualizer

def main():
    st.set_page_config(
        page_title="Real Estate Visualization Demo",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("🏠 Real Estate Data Visualization Demo")
    st.markdown("This demo showcases the visualization capabilities for KFH Real Estate Report data")
    
    # Initialize visualizer
    visualizer = RealEstateVisualizer()
    
    # Sample data sets
    sample_datasets = {
        "Governorate Prices": "Ahmadi: 1250, Hawally: 980, Capital: 2100, Jahra: 750, Mubarak Al-Kabeer: 890, Farwaniya: 1100",
        "Quarterly Trends": "Q1 2023: 372.7, Q2 2023: 385.2, Q3 2023: 398.1, Q4 2023: 410.5, Q1 2025: 425.8",
        "Market Segments": "Private Housing: 38.63, Investment: 25.12, Commercial: 18.45, Coastline: 12.80, Industrial: 5.00",
        "Property Types": "Villa: 45.2, Apartment: 32.8, Townhouse: 15.6, Land: 6.4",
        "Investment Returns": "Residential: 8.5, Commercial: 12.3, Industrial: 15.7, Retail: 10.2, Office: 9.8"
    }
    
    # Sidebar for dataset selection
    st.sidebar.header("📊 Sample Datasets")
    selected_dataset = st.sidebar.selectbox(
        "Choose a dataset:",
        list(sample_datasets.keys())
    )
    
    # Display selected dataset
    st.subheader(f"📋 Dataset: {selected_dataset}")
    sample_data = sample_datasets[selected_dataset]
    st.code(sample_data, language="text")
    
    # Chart type selection
    st.subheader("🎨 Chart Type Selection")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        chart_type = st.selectbox(
            "Select chart type:",
            list(visualizer.chart_types.keys()),
            format_func=lambda x: visualizer.chart_types[x]
        )
    
    with col2:
        st.info(f"Selected: {visualizer.chart_types[chart_type]}")
    
    # Generate and display visualization
    if st.button("🚀 Generate Visualization", type="primary"):
        st.subheader("📈 Generated Chart")
        
        try:
            # Extract data
            data = visualizer.extract_data_from_text(sample_data)
            
            if data['values']:
                # Generate chart
                fig = visualizer.generate_visualization(sample_data, chart_type)
                
                # Display chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Data summary
                st.subheader("📊 Data Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Categories", len(data['categories']))
                
                with col2:
                    st.metric("Total Value", f"{sum(data['values']):,.0f}")
                
                with col3:
                    st.metric("Average", f"{np.mean(data['values']):,.2f}")
                
                with col4:
                    st.metric("Max Value", f"{max(data['values']):,.0f}")
                
                # Data table
                st.subheader("📋 Detailed Data")
                df_summary = pd.DataFrame({
                    'Category': data['categories'],
                    'Value': data['values'],
                    'Percentage': [f"{(v/sum(data['values'])*100):.1f}%" for v in data['values']],
                    'Rank': [i+1 for i in range(len(data['categories']))]
                })
                st.dataframe(df_summary, use_container_width=True)
                
                # Chart suggestions
                st.subheader("💡 Chart Suggestions")
                suggestions = visualizer.get_chart_suggestions(data)
                for suggestion in suggestions:
                    st.write(f"• {suggestion}")
                
                st.success(f"✅ Successfully generated {visualizer.chart_types[chart_type]} with {len(data['categories'])} data points!")
                
            else:
                st.warning("⚠️ No numerical data found in the selected dataset")
                
        except Exception as e:
            st.error(f"❌ Error generating visualization: {e}")
            st.info("Try selecting a different chart type or dataset")
    
    # Interactive demo section
    st.subheader("🎯 Interactive Demo")
    st.markdown("Try entering your own data and see it visualized!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        custom_data = st.text_area(
            "Enter your own data:",
            placeholder="Format: Category: Value, Category: Value...",
            height=100
        )
        
        if st.button("🔍 Analyze Custom Data"):
            if custom_data:
                data = visualizer.extract_data_from_text(custom_data)
                if data['values']:
                    st.success(f"Found {len(data['values'])} data points!")
                    st.write("**Categories:**", ", ".join(data['categories']))
                    st.write("**Values:**", ", ".join(map(str, data['values'])))
                else:
                    st.warning("No numerical data found. Use format: Category: Value, Category: Value...")
            else:
                st.info("Please enter some data to analyze")
    
    with col2:
        st.markdown("**Data Format Examples:**")
        st.markdown("""
        - `A: 100, B: 200, C: 300`
        - `Category = Value`
        - `Name: Number`
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("**🎉 This demo showcases the visualization capabilities integrated into the KFH Real Estate Chat Assistant!**")
    st.markdown("Try asking the chat assistant for charts using phrases like 'Show me a bar chart of...' or 'Create a pie chart for...'")

if __name__ == "__main__":
    main()
