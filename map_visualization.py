import streamlit as st
import pydeck as pdk
import pandas as pd

def create_first_mile_map(df):
    """
    Create the map visualization for first mile analysis
    
    Args:
        df: pandas DataFrame with filtered data
    """
    # Get the cluster setting from session state
    use_clusters = st.session_state.get('first_mile_use_clusters', False)
    
    # Compute map center based on customer coordinates
    center_lat = df['customerlat'].mean()
    center_lon = df['customerlong'].mean()
    
    # 1. Heatmap layer for pickup density
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=df,
        get_position=['customerlong', 'customerlat'],
        opacity=0.6,
        get_weight=1,
        aggregation='"SUM"',
        threshold=0.05,
        radius_pixels=35,
    )
    
    # 2. Microwarehouse layer with Google Maps-style drop pins
    microwarehouse_data = df[['microwarehouse', 'microwarehouselong', 'microwarehouselat']].drop_duplicates()
    
    # Add microwarehouse colors for legend
    if 'color' in df.columns:
        # Create a mapping from microwarehouse to color
        color_map = {}
        microwarehouse_color_df = df[['microwarehouse']].drop_duplicates()
        
        for mw in microwarehouse_color_df['microwarehouse']:
            # Get the first row where microwarehouse equals this value
            row = df[df['microwarehouse'] == mw].iloc[0]
            color_map[mw] = row['color']
        
        microwarehouse_data['color'] = microwarehouse_data['microwarehouse'].map(color_map)
    
    microwarehouse_layer = pdk.Layer(
        "IconLayer",
        data=microwarehouse_data,
        get_position=['microwarehouselong', 'microwarehouselat'],
        get_icon="pin",
        get_size=8,
        size_scale=3,
        get_color=[0, 0, 255, 255],  # Blue for microwarehouses
        pickable=True,
        icon_allow_overlap=True,
    )
    
    # 3. Customer pickup points layer - choose between clustered or individual markers
    if use_clusters:
        # Cluster layer for pickups
        pickup_layer = pdk.Layer(
            "HexagonLayer",
            data=df,
            get_position=['customerlong', 'customerlat'],
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
        # Individual marker layer for pickups
        pickup_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=['customerlong', 'customerlat'],
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
        "html": "<b>Trip ID:</b> {trip_id}<br />"
               "<b>Customer:</b> {customer}<br />"
               "<b>Hub:</b> {hub}<br />"
               "<b>Microwarehouse:</b> {microwarehouse}<br />"
               "<b>Picked up at:</b> {pickedup_at}<br />"
               "<b>Distance:</b> {kms} km<br />"
               "<b>Orders:</b> {num_orders}",
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
    map_title = "First Mile Pickup Heatmap with " + ("Clustered Markers" if use_clusters else "Individual Markers")
    st.markdown(f"### {map_title}")
    
    # For clustered view, adjust layer ordering
    layers = [heatmap_layer, pickup_layer, microwarehouse_layer]
        
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style='light',  # Use default light style instead of mapbox URL
        tooltip=cluster_tooltip
    )
    tooltip = {
        "html": "<b>Trip ID:</b> {trip_id}<br />"
               "<b>Customer:</b> {customer}<br />"
               "<b>Hub:</b> {hub}<br />"
               "<b>Microwarehouse:</b> {microwarehouse}<br />"
               "<b>Picked up at:</b> {pickedup_at}<br />"
               "<b>Distance:</b> {kms} km<br />"
               "<b>Orders:</b> {num_orders}",
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
    map_title = "First Mile Pickup Heatmap with " + ("Clustered Markers" if use_clusters else "Individual Markers")
    st.markdown(f"### {map_title}")
    
    # For clustered view, adjust layer ordering
    layers = [heatmap_layer, pickup_layer, microwarehouse_layer]
        
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/light-v10',
        tooltip=cluster_tooltip
    )
    
    # Display the map
    st.pydeck_chart(deck)
    
    # Create a microwarehouse color legend
    if 'microwarehouse' in df.columns:
        st.markdown("### Microwarehouse Color Legend")
        
        # Get unique microwarehouses only (not including color)
        unique_warehouses = df[['microwarehouse']].drop_duplicates()
        
        # Calculate number of columns based on number of microwarehouses
        num_legend_cols = min(len(unique_warehouses), 4)  # Limit to 4 columns max
        if num_legend_cols > 0:  # Ensure we have at least one column
            legend_cols = st.columns(num_legend_cols)
            
            for i, (_, warehouse_row) in enumerate(unique_warehouses.iterrows()):
                col_idx = i % num_legend_cols
                with legend_cols[col_idx]:
                    # Get the first row with this microwarehouse
                    mw = warehouse_row['microwarehouse']
                    color_row = df[df['microwarehouse'] == mw].iloc[0]
                    
                    # Convert RGB to hex for the colored box
                    color = color_row['color']
                    if isinstance(color, list) and len(color) >= 3:
                        hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
                        st.markdown(f"<div style='background-color: {hex_color}; width: 20px; height: 20px; display: inline-block; margin-right: 5px;'></div> {mw}", unsafe_allow_html=True)


def create_last_mile_map(df):
    """
    Create the map visualization for last mile analysis
    
    Args:
        df: pandas DataFrame with filtered data
    """
    # Get the cluster setting from session state
    use_clusters = st.session_state.get('last_mile_use_clusters', False)
    
    # Compute map center based on delivery coordinates
    center_lat = df['delivered_lat'].mean()
    center_lon = df['delivered_long'].mean()
    
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
    if 'color' in df.columns:
        # Create a mapping from hub to color
        color_map = {}
        hub_color_df = df[['hub']].drop_duplicates()
        
        for hub_name in hub_color_df['hub']:
            # Get the first row where hub equals this value
            row = df[df['hub'] == hub_name].iloc[0]
            color_map[hub_name] = row['color']
        
        hub_data['color'] = hub_data['hub'].map(color_map)
    
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
    map_title = "Last Mile Delivery Heatmap with " + ("Clustered Markers" if use_clusters else "Individual Markers")
    st.markdown(f"### {map_title}")
    
    # Combine layers
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
        
        # Get unique hubs only (without the color column)
        unique_hubs = df[['hub']].drop_duplicates()
        
        # Calculate number of columns based on number of hubs
        num_legend_cols = min(len(unique_hubs), 4)  # Limit to 4 columns max
        if num_legend_cols > 0:  # Ensure we have at least one column
            legend_cols = st.columns(num_legend_cols)
            
            for i, (_, hub_row) in enumerate(unique_hubs.iterrows()):
                col_idx = i % num_legend_cols
                with legend_cols[col_idx]:
                    # Get the first row with this hub
                    hub_name = hub_row['hub']
                    color_row = df[df['hub'] == hub_name].iloc[0]
                    
                    # Convert RGB to hex for the colored box
                    color = color_row['color']
                    if isinstance(color, list) and len(color) >= 3:
                        hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
                        st.markdown(f"<div style='background-color: {hex_color}; width: 20px; height: 20px; display: inline-block; margin-right: 5px;'></div> {hub_name}", unsafe_allow_html=True)
