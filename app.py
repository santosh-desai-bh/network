import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os
import base64

# Set page configuration
st.set_page_config(
    page_title="Delivery Network Analysis",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #0D47A1;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 1rem;
        color: #424242;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown("<h1 class='main-header'>Delivery Network Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("""
This interactive dashboard provides comprehensive insights into your delivery network operations. 
Analyze delivery patterns, hub performance, vehicle utilization, and geographical distribution of your deliveries.
""")

# Sidebar for data upload and filters
st.sidebar.header("Data Input")

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload your delivery data CSV", type=["csv"])

# Function to load sample data if no file is uploaded
@st.cache_data
def load_sample_data():
    # Sample data similar to the structure provided
    data = {
        'number': ['AWBBH1007834', 'AWBBH970817', 'AWBBH1005473', 'SH-2W8MYXI', 'SH-2WDMOA8', 'AWBBH1045072', 'AWBBH970206'],
        'created_date': ["April 14, 2025, 6:31 AM", "April 16, 2025, 11:06 AM", "April 11, 2025, 9:40 PM", 
                         "April 10, 2025, 8:34 PM", "April 15, 2025, 6:34 AM", "April 16, 2025, 10:56 AM", 
                         "April 14, 2025, 10:57 AM"],
        'driver': ['Harikrishna N A', 'Ravi Kumar T', 'Vijay Kumar', 'Bheemana Gouda', 'Ninge Gowda', 'Ravi H N', 'Shantha Kumar S'],
        'registration_certificate_number': ['KA50X2147', 'KA01AE8326', 'KA01AA4196', 'KA03AH0255', 'KA417210', 'KA05AH3317', 'KA40X5524'],
        'vehicle_model': ['Bike', 'Auto Rickshaw', 'Auto Rickshaw', 'Auto Rickshaw', 'Auto Rickshaw', 'Auto Rickshaw', 'Bike'],
        'hub': ['Hebbal [ BH Micro warehouse ]', 'Kudlu [ BH Micro warehouse ]', 'Kudlu [ BH Micro warehouse ]', 
                'Mahadevapura [ BH Micro warehouse ]', 'Banashankari [ BH Micro warehouse ]', 'Hebbal [ BH Micro warehouse ]', 
                'Mahadevapura [ BH Micro warehouse ]'],
        'customer': ['TATA CLiQ', 'WESTSIDE UNIT OF TRENT LIMITED', 'TATA CLiQ', 'Herbalife Nutrition', 
                     'Herbalife Nutrition', 'TATA CLiQ', 'WESTSIDE UNIT OF TRENT LIMITED'],
        'postcode': ['560043', '560068', '560099', '560048', '560050', '560064', '560016'],
        'hub_long': [77.61, 77.67, 77.67, 77.7, 77.6, 77.61, 77.7],
        'hub_lat': [13.07, 12.92, 12.92, 12.97, 12.91, 13.07, 12.97],
        'delivered_long': [77.62, 77.67, 77.68, 77.71, 77.55, 77.56, 77.68],
        'delivered_lat': [13.06, 12.88, 12.87, 12.99, 12.94, 13.11, 12.99],
        'weight': [0.5, 0.3, 0.5, 0.24, 1.48, 0.76, 0.8],
        'kms': [1.98, 4.25, 6.21, 2.45, 5.77, 6.24, 2.79]
    }
    return pd.DataFrame(data)

# Load data
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("Successfully loaded your data!")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
        df = load_sample_data()
        st.sidebar.info("Loaded sample data instead.")
else:
    df = load_sample_data()
    st.sidebar.info("Using sample data. Upload your CSV for custom analysis.")

# Download sample data template
def get_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="sample_delivery_data.csv">Download sample data template</a>'
    return href

st.sidebar.markdown(get_download_link(df), unsafe_allow_html=True)

@st.cache_data
def process_data(df):
    # Copy the dataframe to avoid modification warnings
    processed_df = df.copy()
    
    # Convert created_date to datetime
    try:
        processed_df['created_date'] = pd.to_datetime(processed_df['created_date'], errors='coerce')
    except:
        st.warning("Could not parse date format. Using original format.")
    
    # Clean hub names (remove the "[BH Micro warehouse]" part)
    if 'hub' in processed_df.columns:
        processed_df['hub_clean'] = processed_df['hub'].str.split('[').str[0].str.strip()
    
    # Clean the kms column if it exists
    if 'kms' in processed_df.columns:
        try:
            # First, try to convert directly
            processed_df['kms'] = pd.to_numeric(processed_df['kms'], errors='coerce')
        except:
            # If that fails, try to clean the string values first
            processed_df['kms'] = processed_df['kms'].astype(str)
            # Replace commas and multiple dots with a single dot
            processed_df['kms'] = processed_df['kms'].str.replace(',', '.')
            # Keep only the first decimal point
            processed_df['kms'] = processed_df['kms'].apply(lambda x: x.split('.')[0] + '.' + ''.join(x.split('.')[1:]) if '.' in x else x)
            # Convert to numeric, replacing non-convertible values with NaN
            processed_df['kms'] = pd.to_numeric(processed_df['kms'], errors='coerce')
    
    return processed_df
processed_df = process_data(df)

# Sidebar filters
st.sidebar.header("Filters")

# Date filter if dates are available
if 'created_date' in processed_df.columns and pd.api.types.is_datetime64_any_dtype(processed_df['created_date']):
    min_date = processed_df['created_date'].min().date()
    max_date = processed_df['created_date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (processed_df['created_date'].dt.date >= start_date) & (processed_df['created_date'].dt.date <= end_date)
        filtered_df = processed_df[mask]
    else:
        filtered_df = processed_df
else:
    filtered_df = processed_df

# Hub filter
if 'hub' in filtered_df.columns:
    all_hubs = filtered_df['hub'].unique().tolist()
    selected_hubs = st.sidebar.multiselect("Select Hubs", all_hubs, default=all_hubs)
    
    if selected_hubs:
        filtered_df = filtered_df[filtered_df['hub'].isin(selected_hubs)]

# Vehicle filter
if 'vehicle_model' in filtered_df.columns:
    all_vehicles = filtered_df['vehicle_model'].unique().tolist()
    selected_vehicles = st.sidebar.multiselect("Select Vehicle Types", all_vehicles, default=all_vehicles)
    
    if selected_vehicles:
        filtered_df = filtered_df[filtered_df['vehicle_model'].isin(selected_vehicles)]

# Customer filter
if 'customer' in filtered_df.columns:
    all_customers = filtered_df['customer'].unique().tolist()
    selected_customers = st.sidebar.multiselect("Select Customers", all_customers, default=all_customers)
    
    if selected_customers:
        filtered_df = filtered_df[filtered_df['customer'].isin(selected_customers)]

# Main content with tabs
tab1, tab2, tab3, tab4, tab5, tab6  = st.tabs(["Overview", "Heatmaps", "Geographic Analysis", "Driver Performance", "Data Explorer",
                                               "Pincode Analysis"])

with tab1:
    st.markdown("<h2 class='sub-header'>Delivery Network Overview</h2>", unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>{len(filtered_df)}</div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-label'>Total Deliveries</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        num_hubs = filtered_df['hub'].nunique() if 'hub' in filtered_df.columns else 0
        st.markdown(f"<div class='metric-value'>{num_hubs}</div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-label'>Active Hubs</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        avg_dist = filtered_df['kms'].mean() if 'kms' in filtered_df.columns else 0
        st.markdown(f"<div class='metric-value'>{avg_dist:.2f} km</div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-label'>Avg. Delivery Distance</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        num_drivers = filtered_df['driver'].nunique() if 'driver' in filtered_df.columns else 0
        st.markdown(f"<div class='metric-value'>{num_drivers}</div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-label'>Active Drivers</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Daily delivery trend
    st.markdown("<h3>Delivery Trend</h3>", unsafe_allow_html=True)
    
    if 'created_date' in filtered_df.columns and pd.api.types.is_datetime64_any_dtype(filtered_df['created_date']):
        # Create daily count
        daily_counts = filtered_df.groupby(filtered_df['created_date'].dt.date).size().reset_index()
        daily_counts.columns = ['date', 'count']
        
        fig = px.line(daily_counts, x='date', y='count', 
                     title='Daily Delivery Volumes',
                     labels={'count': 'Number of Deliveries', 'date': 'Date'})
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Deliveries",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Date information not available or could not be parsed.")
    
    # Hub distributions
    if 'hub' in filtered_df.columns:
        st.markdown("<h3>Hub Distribution</h3>", unsafe_allow_html=True)
        
        hub_counts = filtered_df['hub'].value_counts().reset_index()
        hub_counts.columns = ['hub', 'count']
        
        fig = px.bar(hub_counts, x='hub', y='count', 
                    title='Deliveries by Hub',
                    color='count',
                    color_continuous_scale='Blues',
                    labels={'count': 'Number of Deliveries', 'hub': 'Hub'})
        
        fig.update_layout(
            xaxis_title="Hub",
            yaxis_title="Number of Deliveries",
            height=500,
            xaxis={'categoryorder':'total descending'}
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("<h2 class='sub-header'>Heatmap Analysis</h2>", unsafe_allow_html=True)
    
    # Hub-Customer heatmap
    if all(col in filtered_df.columns for col in ['hub', 'customer']):
        st.markdown("<h3>Hub-Customer Delivery Heatmap</h3>", unsafe_allow_html=True)
        
        hub_customer_counts = pd.crosstab(filtered_df['hub'], filtered_df['customer'])
        
        fig = px.imshow(hub_customer_counts, 
                       labels=dict(x="Customer", y="Hub", color="Deliveries"),
                       x=hub_customer_counts.columns,
                       y=hub_customer_counts.index,
                       color_continuous_scale='Blues')
        
        fig.update_layout(
            height=600,
            xaxis={'tickangle': 45}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Hub-Vehicle heatmap
    if all(col in filtered_df.columns for col in ['hub', 'vehicle_model']):
        st.markdown("<h3>Hub-Vehicle Type Heatmap</h3>", unsafe_allow_html=True)
        
        hub_vehicle_counts = pd.crosstab(filtered_df['hub'], filtered_df['vehicle_model'])
        
        fig = px.imshow(hub_vehicle_counts, 
                       labels=dict(x="Vehicle Type", y="Hub", color="Count"),
                       x=hub_vehicle_counts.columns,
                       y=hub_vehicle_counts.index,
                       color_continuous_scale='Greens')
        
        fig.update_layout(
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Distance heatmap by hub
    if all(col in filtered_df.columns for col in ['hub', 'kms']):
        st.markdown("<h3>Average Delivery Distance by Hub</h3>", unsafe_allow_html=True)
        
        hub_distance = filtered_df.groupby('hub')['kms'].mean().reset_index()
        hub_distance = hub_distance.sort_values('kms', ascending=False)
        
        fig = px.bar(hub_distance, x='hub', y='kms',
                    title='Average Distance by Hub',
                    color='kms',
                    color_continuous_scale='Reds',
                    labels={'kms': 'Average Distance (km)', 'hub': 'Hub'})
        
        fig.update_layout(
            height=500,
            xaxis={'categoryorder':'total descending'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Weight heatmap by hub
    if all(col in filtered_df.columns for col in ['hub', 'weight']):
        st.markdown("<h3>Average Package Weight by Hub</h3>", unsafe_allow_html=True)
        
        hub_weight = filtered_df.groupby('hub')['weight'].mean().reset_index()
        hub_weight = hub_weight.sort_values('weight', ascending=False)
        
        fig = px.bar(hub_weight, x='hub', y='weight',
                    title='Average Package Weight by Hub',
                    color='weight',
                    color_continuous_scale='Purples',
                    labels={'weight': 'Average Weight (kg)', 'hub': 'Hub'})
        
        fig.update_layout(
            height=500,
            xaxis={'categoryorder':'total descending'}
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("<h2 class='sub-header'>Geographic Analysis</h2>", unsafe_allow_html=True)
    
    # Map showing hubs and delivery locations
    if all(col in filtered_df.columns for col in ['hub_lat', 'hub_long', 'delivered_lat', 'delivered_long']):
        st.markdown("<h3>Delivery Network Map</h3>", unsafe_allow_html=True)
        
        # Create a Folium map centered around the average of hub locations
        map_center = [filtered_df['hub_lat'].mean(), filtered_df['hub_long'].mean()]
        delivery_map = folium.Map(location=map_center, zoom_start=12)
        
        # Add hub locations
        for _, row in filtered_df.drop_duplicates('hub').iterrows():
            folium.Marker(
                location=[row['hub_lat'], row['hub_long']],
                popup=row['hub'],
                icon=folium.Icon(color='blue', icon='home')
            ).add_to(delivery_map)
        
        # Add a heatmap of all delivery locations
        heat_data = [[row['delivered_lat'], row['delivered_long']] for _, row in filtered_df.iterrows()]
        HeatMap(heat_data).add_to(delivery_map)
        
        # Display the map
        folium_static(delivery_map)
        
        # Hub activity map
        st.markdown("<h3>Hub Activity Heatmap</h3>", unsafe_allow_html=True)
        
        hub_activity = filtered_df.groupby(['hub', 'hub_lat', 'hub_long']).size().reset_index()
        hub_activity.columns = ['hub', 'lat', 'lon', 'count']
        
        fig = px.density_mapbox(hub_activity, lat='lat', lon='lon', z='count', radius=30,
                              center=dict(lat=map_center[0], lon=map_center[1]), zoom=10,
                              mapbox_style="carto-positron",
                              labels={'count': 'Number of Deliveries'})
        
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Geographic data (latitude/longitude) not available.")

with tab4:
    st.markdown("<h2 class='sub-header'>Driver Performance Analysis</h2>", unsafe_allow_html=True)
    
    if 'driver' in filtered_df.columns:
        # Driver delivery counts
        driver_counts = filtered_df['driver'].value_counts().reset_index()
        driver_counts.columns = ['driver', 'deliveries']
        
        # Driver average distance
        if 'kms' in filtered_df.columns:
            driver_dist = filtered_df.groupby('driver')['kms'].mean().reset_index()
            driver_dist.columns = ['driver', 'avg_distance']
            
            # Merge the data
            driver_data = pd.merge(driver_counts, driver_dist, on='driver')
            
            # Top drivers by deliveries
            st.markdown("<h3>Top Drivers by Number of Deliveries</h3>", unsafe_allow_html=True)
            
            top_drivers = driver_data.sort_values('deliveries', ascending=False).head(10)
            
            fig = px.bar(top_drivers, x='driver', y='deliveries',
                        color='deliveries',
                        color_continuous_scale='Blues',
                        labels={'deliveries': 'Number of Deliveries', 'driver': 'Driver'})
            
            fig.update_layout(
                height=500,
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Driver efficiency (deliveries per km)
            st.markdown("<h3>Driver Efficiency (Average Distance per Delivery)</h3>", unsafe_allow_html=True)
            
            driver_data['efficiency'] = driver_data['avg_distance']
            driver_efficiency = driver_data.sort_values('efficiency').head(10)
            
            fig = px.bar(driver_efficiency, x='driver', y='efficiency',
                        color='efficiency',
                        color_continuous_scale='RdYlGn_r',  # Reversed so lower (better) is green
                        labels={'efficiency': 'Avg. Distance per Delivery (km)', 'driver': 'Driver'})
            
            fig.update_layout(
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<h3>Driver Performance</h3>", unsafe_allow_html=True)
            
            fig = px.bar(driver_counts.head(10), x='driver', y='deliveries',
                        color='deliveries',
                        color_continuous_scale='Blues',
                        labels={'deliveries': 'Number of Deliveries', 'driver': 'Driver'})
            
            fig.update_layout(
                height=500,
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Driver information not available.")

with tab5:
    st.markdown("<h2 class='sub-header'>Data Explorer</h2>", unsafe_allow_html=True)
    
    # Show raw data
    st.markdown("<h3>Raw Data</h3>", unsafe_allow_html=True)
    st.write(filtered_df)
    
    # Data statistics
    st.markdown("<h3>Data Statistics</h3>", unsafe_allow_html=True)
    
    numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if numeric_cols:
        stats_df = filtered_df[numeric_cols].describe().round(2)
        st.write(stats_df)
    else:
        st.info("No numeric columns available for statistics.")
    
    # Correlation heatmap
    if len(numeric_cols) > 1:
        st.markdown("<h3>Correlation Heatmap</h3>", unsafe_allow_html=True)
        
        corr = filtered_df[numeric_cols].corr()
        
        fig = px.imshow(corr,
                       labels=dict(color="Correlation"),
                       x=corr.columns,
                       y=corr.columns,
                       color_continuous_scale='RdBu_r',
                       zmin=-1, zmax=1)
        
        fig.update_layout(
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
with tab6:
    st.markdown("<h2 class='sub-header'>Pincode Analysis</h2>", unsafe_allow_html=True)
    
    if 'postcode' in filtered_df.columns:
        # Pincode distribution
        st.markdown("<h3>Delivery Distribution by Pincode</h3>", unsafe_allow_html=True)
        
        # Count deliveries by pincode
        pincode_counts = filtered_df['postcode'].value_counts().reset_index()
        pincode_counts.columns = ['pincode', 'count']
        
        # Top 20 pincodes by delivery count
        top_pincodes = pincode_counts.head(20)
        
        fig = px.bar(top_pincodes, x='pincode', y='count',
                    title='Top Pincodes by Number of Deliveries',
                    color='count',
                    color_continuous_scale='Viridis',
                    labels={'count': 'Number of Deliveries', 'pincode': 'Pincode'})
        
        fig.update_layout(
            height=500,
            xaxis={'categoryorder':'total descending'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Delivery metrics by pincode
        st.markdown("<h3>Delivery Metrics by Pincode</h3>", unsafe_allow_html=True)
        
        # First, get the count of deliveries per pincode
        pincode_metrics = filtered_df.groupby('postcode').size().reset_index()
        pincode_metrics.columns = ['postcode', 'count']
        
        # Add average distance if kms column exists
        if 'kms' in filtered_df.columns:
            avg_distance = filtered_df.groupby('postcode')['kms'].mean().reset_index()
            avg_distance.columns = ['postcode', 'avg_distance']
            pincode_metrics = pd.merge(pincode_metrics, avg_distance, on='postcode')
            pincode_metrics['avg_distance'] = pincode_metrics['avg_distance'].round(2)
            
        # Add average weight if weight column exists
        if 'weight' in filtered_df.columns:
            avg_weight = filtered_df.groupby('postcode')['weight'].mean().reset_index()
            avg_weight.columns = ['postcode', 'avg_weight']
            pincode_metrics = pd.merge(pincode_metrics, avg_weight, on='postcode')
            pincode_metrics['avg_weight'] = pincode_metrics['avg_weight'].round(2)
        
        # Sort by delivery count (descending)
        pincode_metrics = pincode_metrics.sort_values('count', ascending=False)
        
        # Show the table
        st.dataframe(pincode_metrics)
        
        # Hub-Pincode heatmap
        if 'hub' in filtered_df.columns:
            st.markdown("<h3>Hub-Pincode Delivery Heatmap</h3>", unsafe_allow_html=True)
            
            # Get top 15 pincodes for better visualization
            top_15_pincodes = pincode_counts.head(15)['pincode'].tolist()
            hub_pincode_df = filtered_df[filtered_df['postcode'].isin(top_15_pincodes)]
            
            hub_pincode_counts = pd.crosstab(hub_pincode_df['hub'], hub_pincode_df['postcode'])
            
            fig = px.imshow(hub_pincode_counts, 
                          labels=dict(x="Pincode", y="Hub", color="Deliveries"),
                          x=hub_pincode_counts.columns,
                          y=hub_pincode_counts.index,
                          color_continuous_scale='Purples')
            
            fig.update_layout(
                height=600,
                xaxis={'tickangle': 45}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        # Customer-Pincode analysis
        if 'customer' in filtered_df.columns:
            st.markdown("<h3>Customer Presence by Pincode</h3>", unsafe_allow_html=True)
            
            # Get top 10 customers
            top_customers = filtered_df['customer'].value_counts().head(10).index.tolist()
            
            # Filter for top customers
            top_customer_df = filtered_df[filtered_df['customer'].isin(top_customers)]
            
            # Get unique pincodes per customer
            customer_pincode_data = []
            for customer in top_customers:
                customer_data = top_customer_df[top_customer_df['customer'] == customer]
                pincodes_count = customer_data['postcode'].nunique()
                customer_pincode_data.append({
                    'customer': customer,
                    'unique_pincodes': pincodes_count
                })
            
            customer_pincodes_df = pd.DataFrame(customer_pincode_data)
            
            fig = px.bar(customer_pincodes_df, x='customer', y='unique_pincodes',
                        title='Number of Unique Pincodes Served by Top Customers',
                        color='unique_pincodes',
                        color_continuous_scale='Teal',
                        labels={'unique_pincodes': 'Number of Unique Pincodes', 'customer': 'Customer'})
            
            fig.update_layout(
                height=500,
                xaxis={'categoryorder':'total descending', 'tickangle': 45}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pincode information not available in the dataset.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Delivery Network Analysis Dashboard | Created with Streamlit</p>
</div>
""", unsafe_allow_html=True)
