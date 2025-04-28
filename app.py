import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Delivery Heatmap Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a title
st.title("Delivery Heatmap Dashboard")

# Add custom help text with the download link
st.markdown("""
### Download the data
Please download the CSV data from: 
[Network Analysis Query](https://analytics.blowhorn.com/question/3120-if-network-analysis-last-mile?start=2025-04-01&end=2025-04-28)

After downloading, upload the CSV file below:
""")

# File uploader for the CSV data
uploaded_file = st.file_uploader("Upload delivery data CSV", type=["csv"])

if uploaded_file is not None:
    # Load the data
    df = pd.read_csv(uploaded_file)
    
    # Check if the necessary columns exist
    required_columns = ['hub_long', 'hub_lat', 'delivered_long', 'delivered_lat']
    if all(col in df.columns for col in required_columns):
        # Convert date column if it exists
        if 'created_date' in df.columns:
            df['created_date'] = pd.to_datetime(df['created_date'])
        
        # Convert numeric columns from strings to floats
        numeric_columns = ['hub_long', 'hub_lat', 'delivered_long', 'delivered_lat', 'kms']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Display basic information
        st.sidebar.markdown("## Data Summary")
        st.sidebar.write(f"Total Deliveries: {len(df)}")
        if 'created_date' in df.columns:
            st.sidebar.write(f"Date Range: {df['created_date'].min().date()} to {df['created_date'].max().date()}")
        
        # Filter by hub if the column exists
        if 'hub' in df.columns:
            all_hubs = sorted(df['hub'].unique().tolist())
            selected_hubs = st.sidebar.multiselect(
                "Filter by Hub",
                options=all_hubs,
                default=all_hubs
            )
            
            if selected_hubs:
                df = df[df['hub'].isin(selected_hubs)]
        
        # Filter by pincode if the column exists
        if 'postcode' in df.columns:
            # Convert postcode to string if it's not already
            df['postcode'] = df['postcode'].astype(str)
            
            # Get unique pincodes with their respective hubs
            pincode_hub_map = df.groupby('postcode')['hub'].unique().apply(lambda x: ', '.join(x)).reset_index()
            pincode_hub_map.columns = ['Pincode', 'Serving Hubs']
            
            # Create a selectbox for choosing pincode
            all_pincodes = ["All"] + sorted(df['postcode'].unique().tolist())
            selected_pincode = st.sidebar.selectbox(
                "Filter by Pincode",
                options=all_pincodes
            )
            
            if selected_pincode != "All":
                df = df[df['postcode'] == selected_pincode]
                # Show pincode details
                pincode_details = pincode_hub_map[pincode_hub_map['Pincode'] == selected_pincode]
                if not pincode_details.empty:
                    st.sidebar.markdown(f"**Pincode {selected_pincode} is served by:**")
                    st.sidebar.write(pincode_details['Serving Hubs'].iloc[0])
                
                # Count deliveries for this pincode
                delivery_count = len(df)
                st.sidebar.markdown(f"**Number of deliveries:** {delivery_count}")
                
                # Calculate average distance for this pincode
                if 'kms' in df.columns:
                    try:
                        avg_dist = round(df['kms'].mean(), 2)
                        st.sidebar.markdown(f"**Average delivery distance:** {avg_dist} km")
                    except:
                        pass
        
        # Filter by vehicle model if the column exists
        if 'vehicle_model' in df.columns:
            all_vehicles = sorted(df['vehicle_model'].unique().tolist())
            selected_vehicles = st.sidebar.multiselect(
                "Filter by Vehicle Type",
                options=all_vehicles,
                default=all_vehicles
            )
            
            if selected_vehicles:
                df = df[df['vehicle_model'].isin(selected_vehicles)]
        
        # Drop rows with NaN values in coordinate columns to avoid map errors
        df = df.dropna(subset=['hub_long', 'hub_lat', 'delivered_long', 'delivered_lat'])
        
        # Create color mapping for hubs
        if 'hub' in df.columns:
            unique_hubs = df['hub'].unique()
            colors = {}
            
            # Generate distinct colors for each hub
            for i, hub in enumerate(unique_hubs):
                # Create colors with good separation (using HSL color space logic)
                hue = (i * 137.5) % 360  # Use golden angle to get good separation
                colors[hub] = [
                    int(255 * (0.7 + 0.3 * np.sin(np.radians(hue)))),  # R
                    int(255 * (0.7 + 0.3 * np.sin(np.radians(hue + 120)))),  # G
                    int(255 * (0.7 + 0.3 * np.sin(np.radians(hue + 240)))),  # B
                    180  # Alpha
                ]
            
            # Add color column to dataframe
            df['color'] = df['hub'].map(lambda x: colors.get(x, [100, 100, 100, 180]))
        else:
            # Default color if no hub column
            df['color'] = [[100, 100, 100, 180]] * len(df)
        
        # Compute map center
        center_lat = df['delivered_lat'].mean()
        center_lon = df['delivered_long'].mean()
        
        # Add toggle for marker clustering vs individual markers
        st.sidebar.markdown("## Map Settings")
        use_clusters = st.sidebar.toggle("Use Marker Clusters", value=False)
        
        # 1. Heatmap layer for delivery density
        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=df,
            get_position=['delivered_long', 'delivered_lat'],
            opacity=0.6,
            get_weight=1,
            aggregation='"SUM"',
            threshold=0.05,
            radius_pixels=35,
        )
        
        # 2. Hub layer with Google Maps-style drop pins
        hub_data = df[['hub', 'hub_long', 'hub_lat']].drop_duplicates()
        
        # Add hub colors for legend
        if 'hub' in df.columns:
            hub_data['color'] = hub_data['hub'].map(lambda x: colors.get(x, [100, 100, 100, 180]))
        
        hub_layer = pdk.Layer(
            "IconLayer",
            data=hub_data,
            get_position=['hub_long', 'hub_lat'],
            get_icon="pin",
            get_size=8,
            size_scale=3,
            get_color=[255, 0, 0, 255],  # Red for hubs
            pickable=True,
            icon_allow_overlap=True,
        )
        
        # 3. Delivery points layer - choose between clustered or individual markers
        if use_clusters:
            # Cluster layer for deliveries
            delivery_layer = pdk.Layer(
                "HexagonLayer",
                data=df,
                get_position=['delivered_long', 'delivered_lat'],
                radius=200,  # Hex cell size
                elevation_scale=5,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
                auto_highlight=True,
                coverage=1,
                get_color='color',  # Use the color mapping we created
            )
        else:
            # Individual marker layer for deliveries
            delivery_layer = pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position=['delivered_long', 'delivered_lat'],
                get_radius=75,
                get_fill_color='color',  # Use the color mapping we created
                pickable=True,
                opacity=0.8,
                stroked=True,
                filled=True,
                radius_min_pixels=4,
                radius_max_pixels=8,
            )
        
        # Set the initial view state
        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=10,
            pitch=0 if not use_clusters else 40,  # Add tilt when using clusters
        )
        
        # Create tooltip
        tooltip = {
            "html": "<b>Order:</b> {number}<br />"
                   "<b>Hub:</b> {hub}<br />"
                   "<b>Customer:</b> {customer}<br />"
                   "<b>Driver:</b> {driver}<br />"
                   "<b>Distance:</b> {kms} km"
                   + ("<br /><b>Pincode:</b> {postcode}" if 'postcode' in df.columns else ""),
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        }
        
        # Different tooltip for clusters
        cluster_tooltip = {
            "html": "<b>Point Count:</b> {pointCount}"
        } if use_clusters else tooltip
        
        # Combine layers
        map_title = "Delivery Heatmap with " + ("Clustered Markers" if use_clusters else "Individual Markers")
        st.markdown(f"### {map_title}")
        
        # For clustered view, adjust layer ordering
        if use_clusters:
            layers = [heatmap_layer, delivery_layer, hub_layer]
        else:
            layers = [heatmap_layer, delivery_layer, hub_layer]
            
        deck = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/light-v10',
            tooltip=cluster_tooltip
        )
        
        # Display the map
        st.pydeck_chart(deck)
        
        # Create a hub color legend
        if 'hub' in df.columns:
            st.markdown("### Hub Color Legend")
            # Calculate number of columns based on number of hubs
            num_legend_cols = min(len(colors), 4)  # Limit to 4 columns max
            legend_cols = st.columns(num_legend_cols)
            
            for i, (hub, color) in enumerate(colors.items()):
                col_idx = i % num_legend_cols
                with legend_cols[col_idx]:
                    # Convert RGB to hex for the colored box
                    hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
                    st.markdown(f"<div style='background-color: {hex_color}; width: 20px; height: 20px; display: inline-block; margin-right: 5px;'></div> {hub}", unsafe_allow_html=True)
        
        # Create two columns for basic stats
        col1, col2 = st.columns(2)
        
        with col1:
            # Distance distribution
            if 'kms' in df.columns:
                fig = px.histogram(
                    df, 
                    x="kms", 
                    nbins=20,
                    title="Delivery Distance Distribution",
                    labels={"kms": "Distance (km)"},
                    color_discrete_sequence=['#3366CC']
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Hub order counts
            if 'hub' in df.columns:
                hub_counts = df['hub'].value_counts().reset_index()
                hub_counts.columns = ['Hub', 'Deliveries']
                
                # Use the same colors from the map for consistency
                hub_colors = [colors.get(hub, [100, 100, 100])[:3] for hub in hub_counts['Hub']]
                hub_hex_colors = ["#{:02x}{:02x}{:02x}".format(r, g, b) for r, g, b in hub_colors]
                
                fig = px.bar(
                    hub_counts,
                    x='Hub',
                    y='Deliveries',
                    title="Deliveries per Hub",
                    color='Hub',
                    color_discrete_sequence=hub_hex_colors
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # Pincode Analysis
        if 'postcode' in df.columns:
            st.markdown("### Pincode Analysis")
            
            # Get top pincodes by delivery count
            pincode_counts = df['postcode'].value_counts().reset_index()
            pincode_counts.columns = ['Pincode', 'Deliveries']
            
            # If there are many pincodes, just show top 15
            if len(pincode_counts) > 15:
                display_pincodes = pincode_counts.head(15)
                show_more = st.checkbox("Show all pincodes")
                if show_more:
                    display_pincodes = pincode_counts
            else:
                display_pincodes = pincode_counts
            
            # Display pincode statistics
            col1, col2 = st.columns(2)
            
            with col1:
                # Pincode delivery counts
                fig = px.bar(
                    display_pincodes,
                    x='Pincode',
                    y='Deliveries',
                    title="Deliveries by Pincode",
                    color='Deliveries',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Pincode to hub mapping
                if 'hub' in df.columns:
                    # Group pincodes by hub
                    hub_pincode_data = []
                    for hub in df['hub'].unique():
                        hub_pincodes = df[df['hub'] == hub]['postcode'].unique()
                        for pincode in hub_pincodes:
                            count = len(df[(df['hub'] == hub) & (df['postcode'] == pincode)])
                            hub_pincode_data.append({
                                'Hub': hub,
                                'Pincode': pincode,
                                'Deliveries': count
                            })
                    
                    if hub_pincode_data:
                        hub_pincode_df = pd.DataFrame(hub_pincode_data)
                        
                        # Show table of hub-pincode mappings
                        st.markdown("#### Hub-Pincode Mapping")
                        st.dataframe(hub_pincode_df)
            
            # Show detailed pincode table
            st.markdown("#### Pincode Coverage Details")
            
            # Calculate average distance for each pincode
            pincode_stats = df.groupby('postcode').agg({
                'kms': ['mean', 'min', 'max', 'count']
            }).reset_index()
            
            pincode_stats.columns = ['Pincode', 'Avg Distance (km)', 'Min Distance (km)', 'Max Distance (km)', 'Delivery Count']
            pincode_stats = pincode_stats.round(2)
            
            # Join with hub information
            pincode_hub_counts = df.groupby(['postcode', 'hub']).size().reset_index()
            pincode_hub_counts.columns = ['Pincode', 'Hub', 'Count']
            
            # Get the primary hub for each pincode (hub with most deliveries)
            primary_hubs = pincode_hub_counts.sort_values('Count', ascending=False).drop_duplicates('Pincode')[['Pincode', 'Hub']]
            primary_hubs.columns = ['Pincode', 'Primary Hub']
            
            # Merge with stats
            pincode_stats = pincode_stats.merge(primary_hubs, on='Pincode', how='left')
            
            # Display the table
            st.dataframe(pincode_stats)
        
        # Show key metrics in a row of metrics
        st.markdown("### Key Metrics")
        
        metrics_row = st.columns(4)
        
        with metrics_row[0]:
            st.metric("Total Deliveries", f"{len(df)}")
        
        with metrics_row[1]:
            if 'kms' in df.columns:
                try:
                    avg_distance = round(df['kms'].mean(), 2)
                    st.metric("Avg. Distance (km)", f"{avg_distance}")
                except:
                    st.metric("Avg. Distance (km)", "N/A")
        
        with metrics_row[2]:
            if 'driver' in df.columns:
                driver_count = df['driver'].nunique()
                st.metric("Unique Drivers", f"{driver_count}")
        
        with metrics_row[3]:
            if 'postcode' in df.columns:
                pincode_count = df['postcode'].nunique()
                st.metric("Unique Pincodes", f"{pincode_count}")
        
    else:
        missing_cols = [col for col in required_columns if col not in df.columns]
        st.error(f"CSV is missing required columns: {', '.join(missing_cols)}")
        st.info("Required columns: hub_long, hub_lat, delivered_long, delivered_lat")

else:
    st.info("""
    Please follow these steps:
    
    1. Go to [Network Analysis Query](https://analytics.blowhorn.com/question/3120-if-network-analysis-last-mile?start=2025-04-01&end=2025-04-28)
    2. Adjust the date range parameters as needed
    3. Download the results as CSV
    4. Upload the CSV file using the uploader above
    """)
