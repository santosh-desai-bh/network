import streamlit as st
from datetime import datetime

from data_loader import load_data, preprocess_data, detect_data_type
from data_filters import create_first_mile_filters, create_last_mile_filters
from map_visualization import create_first_mile_map, create_last_mile_map
from analytics import (
    create_first_mile_metrics, create_first_mile_charts, create_first_mile_analysis,
    create_last_mile_metrics, create_last_mile_charts, create_last_mile_analysis
)
from utils import set_page_config

def main():
    # Set page configuration
    set_page_config()
    
    # Add tabs for First Mile and Last Mile analysis
    tab1, tab2 = st.tabs(["First Mile Analysis", "Last Mile Analysis"])
    
    with tab1:
        # First Mile Analysis
        st.title("First Mile Pickup Heatmap Dashboard")
        
        # Add custom help text with the download link
        st.markdown("""
        ### Download the data
        Please download the CSV data from: 
        [First Mile Analysis Query](https://analytics.blowhorn.com/question/actual_pickups?start=2025-04-01&end=2025-04-28)
        
        After downloading, upload the CSV file below:
        """)
        
        # File uploader for the CSV data
        first_mile_file = st.file_uploader("Upload pickup data CSV", type=["csv"], key="first_mile_uploader")
        
        if first_mile_file is not None:
            # Load the data
            df = load_data(first_mile_file)
            
            # Detect data type to verify it's first mile data
            data_type = detect_data_type(df)
            
            if data_type == "first_mile":
                # Check if the necessary columns exist
                required_columns = ['microwarehouselong', 'microwarehouselat', 'customerlong', 'customerlat']
                if all(col in df.columns for col in required_columns):
                    # Preprocess the data
                    df = preprocess_data(df, data_type)
                    
                    # Create filters in the sidebar
                    filtered_df = create_first_mile_filters(df)
                    
                    # If data exists after filtering, create visualizations
                    if not filtered_df.empty:
                        # Create the map
                        create_first_mile_map(filtered_df)
                        
                        # Create metrics
                        create_first_mile_metrics(filtered_df)
                        
                        # Create charts
                        create_first_mile_charts(filtered_df)
                        
                        # Create additional analysis if applicable
                        if 'hub' in filtered_df.columns:
                            create_first_mile_analysis(filtered_df)
                else:
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    st.error(f"CSV is missing required columns: {', '.join(missing_cols)}")
                    st.info("Required columns: microwarehouselong, microwarehouselat, customerlong, customerlat")
            else:
                st.error("The uploaded file appears to be last mile delivery data. Please upload first mile pickup data or switch to the Last Mile Analysis tab.")
        else:
            st.info("""
            Please follow these steps:
            
            1. Go to [First Mile Analysis Query](https://analytics.blowhorn.com/question/actual_pickups?start=2025-04-01&end=2025-04-28)
            2. Adjust the date range parameters as needed
            3. Download the results as CSV
            4. Upload the CSV file using the uploader above
            """)
    
    with tab2:
        # Last Mile Analysis
        st.title("Last Mile Delivery Heatmap Dashboard")
        
        # Add custom help text with the download link
        st.markdown("""
        ### Download the data
        Please download the CSV data from: 
        [Last Mile Analysis Query](https://analytics.blowhorn.com/question/3120-if-network-analysis-last-mile?start=2025-04-01&end=2025-04-28)
        
        After downloading, upload the CSV file below:
        """)
        
        # File uploader for the CSV data
        last_mile_file = st.file_uploader("Upload delivery data CSV", type=["csv"], key="last_mile_uploader")
        
        if last_mile_file is not None:
            # Load the data
            df = load_data(last_mile_file)
            
            # Detect data type to verify it's last mile data
            data_type = detect_data_type(df)
            
            if data_type == "last_mile":
                # Check if the necessary columns exist
                required_columns = ['hub_long', 'hub_lat', 'delivered_long', 'delivered_lat']
                if all(col in df.columns for col in required_columns):
                    # Preprocess the data
                    df = preprocess_data(df, data_type)
                    
                    # Create filters in the sidebar
                    filtered_df = create_last_mile_filters(df)
                    
                    # If data exists after filtering, create visualizations
                    if not filtered_df.empty:
                        # Create the map
                        create_last_mile_map(filtered_df)
                        
                        # Create metrics
                        create_last_mile_metrics(filtered_df)
                        
                        # Create charts
                        create_last_mile_charts(filtered_df)
                        
                        # Create pincode analysis if applicable
                        if 'postcode' in filtered_df.columns:
                            create_last_mile_analysis(filtered_df)
                else:
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    st.error(f"CSV is missing required columns: {', '.join(missing_cols)}")
                    st.info("Required columns: hub_long, hub_lat, delivered_long, delivered_lat")
            else:
                st.error("The uploaded file appears to be first mile pickup data. Please upload last mile delivery data or switch to the First Mile Analysis tab.")
        else:
            st.info("""
            Please follow these steps:
            
            1. Go to [Last Mile Analysis Query](https://analytics.blowhorn.com/question/3120-if-network-analysis-last-mile?start=2025-04-01&end=2025-04-28)
            2. Adjust the date range parameters as needed
            3. Download the results as CSV
            4. Upload the CSV file using the uploader above
            """)

if __name__ == "__main__":
    main()
