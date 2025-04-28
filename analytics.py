import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# First Mile Analytics Functions
def create_first_mile_metrics(df):
    """
    Create key metrics display for first mile
    
    Args:
        df: pandas DataFrame with filtered data
    """
    st.markdown("### Key Metrics")
    
    metrics_row = st.columns(4)
    
    with metrics_row[0]:
        st.metric("Total Pickups", f"{len(df)}")
    
    with metrics_row[1]:
        if 'kms' in df.columns:
            try:
                avg_distance = round(df['kms'].mean(), 2)
                st.metric("Avg. Distance (km)", f"{avg_distance}")
            except:
                st.metric("Avg. Distance (km)", "N/A")
    
    with metrics_row[2]:
        if 'customer' in df.columns:
            customer_count = df['customer'].nunique()
            st.metric("Unique Customers", f"{customer_count}")
    
    with metrics_row[3]:
        if 'num_orders' in df.columns:
            total_orders = df['num_orders'].sum()
            st.metric("Total Orders", f"{total_orders}")


def create_first_mile_charts(df):
    """
    Create charts for first mile data analysis
    
    Args:
        df: pandas DataFrame with filtered data
    """
    # Create two columns for basic stats
    col1, col2 = st.columns(2)
    
    with col1:
        # Distance distribution
        if 'kms' in df.columns:
            fig = px.histogram(
                df, 
                x="kms", 
                nbins=20,
                title="Pickup Distance Distribution",
                labels={"kms": "Distance (km)"},
                color_discrete_sequence=['#3366CC']
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Microwarehouse order counts
        if 'microwarehouse' in df.columns:
            mw_counts = df['microwarehouse'].value_counts().reset_index()
            mw_counts.columns = ['Microwarehouse', 'Pickups']
            
            # Map colors to microwarehouses for consistency with the map
            mw_colors = []
            for mw in mw_counts['Microwarehouse']:
                # Get the first color for this microwarehouse - need to handle if color is a list
                mw_rows = df[df['microwarehouse'] == mw]
                if not mw_rows.empty:
                    color_val = mw_rows['color'].iloc[0]
                    if isinstance(color_val, list) and len(color_val) >= 3:
                        mw_colors.append("#{:02x}{:02x}{:02x}".format(color_val[0], color_val[1], color_val[2]))
                    else:
                        mw_colors.append("#646464")  # Default gray color
                else:
                    mw_colors.append("#646464")  # Default if no matching rows
            
            fig = px.bar(
                mw_counts,
                x='Microwarehouse',
                y='Pickups',
                title="Pickups per Microwarehouse",
                color='Microwarehouse',
                color_discrete_sequence=mw_colors
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    # Orders per customer
    if 'customer' in df.columns and 'num_orders' in df.columns:
        st.markdown("### Customer Analysis")
        
        # Group by customer and sum orders
        customer_orders = df.groupby('customer')['num_orders'].sum().reset_index()
        customer_orders.columns = ['Customer', 'Total Orders']
        customer_orders = customer_orders.sort_values('Total Orders', ascending=False)
        
        # If there are many customers, just show top 15
        if len(customer_orders) > 15:
            display_customers = customer_orders.head(15)
            show_more = st.checkbox("Show all customers", key="first_mile_customers")
            if show_more:
                display_customers = customer_orders
        else:
            display_customers = customer_orders
        
        # Plot customer orders
        fig = px.bar(
            display_customers,
            x='Customer',
            y='Total Orders',
            title="Orders by Customer",
            color='Total Orders',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def create_first_mile_analysis(df):
    """
    Create hub analysis for first mile data
    
    Args:
        df: pandas DataFrame with filtered data
    """
    if 'hub' in df.columns:
        st.markdown("### Hub Analysis")
        
        # Group by hub to get pickup stats
        hub_stats = df.groupby('hub').agg({
            'kms': ['mean', 'min', 'max', 'count'],
            'num_orders': ['sum', 'mean']
        }).reset_index()
        
        # Flatten multi-index columns
        hub_stats.columns = ['Hub', 'Avg Distance (km)', 'Min Distance (km)', 'Max Distance (km)', 
                            'Pickup Count', 'Total Orders', 'Avg Orders per Pickup']
        
        # Round numeric columns
        hub_stats = hub_stats.round(2)
        
        # Show hub stats table
        st.dataframe(hub_stats)
        
        # Create hub to microwarehouse mapping
        if 'microwarehouse' in df.columns:
            # Group hubs by microwarehouse
            hub_mw_data = []
            for hub in df['hub'].unique():
                hub_microwarehouses = df[df['hub'] == hub]['microwarehouse'].unique()
                for mw in hub_microwarehouses:
                    count = len(df[(df['hub'] == hub) & (df['microwarehouse'] == mw)])
                    orders = df[(df['hub'] == hub) & (df['microwarehouse'] == mw)]['num_orders'].sum()
                    hub_mw_data.append({
                        'Hub': hub,
                        'Microwarehouse': mw,
                        'Pickups': count,
                        'Total Orders': orders
                    })
            
            if hub_mw_data:
                hub_mw_df = pd.DataFrame(hub_mw_data)
                
                # Show table of hub-microwarehouse mappings
                st.markdown("#### Hub-Microwarehouse Mapping")
                st.dataframe(hub_mw_df)

# Last Mile Analytics Functions
def create_last_mile_metrics(df):
    """
    Create key metrics display for last mile
    
    Args:
        df: pandas DataFrame with filtered data
    """
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


def create_last_mile_charts(df):
    """
    Create charts for last mile data analysis
    
    Args:
        df: pandas DataFrame with filtered data
    """
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
            hub_colors = []
            for hub in hub_counts['Hub']:
                # Get the first color for this hub - need to handle if color is a list
                hub_rows = df[df['hub'] == hub]
                if not hub_rows.empty:
                    color_val = hub_rows['color'].iloc[0]
                    if isinstance(color_val, list) and len(color_val) >= 3:
                        hub_colors.append("#{:02x}{:02x}{:02x}".format(color_val[0], color_val[1], color_val[2]))
                    else:
                        hub_colors.append("#646464")  # Default gray color
                else:
                    hub_colors.append("#646464")  # Default if no matching rows
            
            fig = px.bar(
                hub_counts,
                x='Hub',
                y='Deliveries',
                title="Deliveries per Hub",
                color='Hub',
                color_discrete_sequence=hub_colors
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    # Vehicle model analysis if available
    if 'vehicle_model' in df.columns:
        st.markdown("### Vehicle Analysis")
        
        vehicle_counts = df['vehicle_model'].value_counts().reset_index()
        vehicle_counts.columns = ['Vehicle Type', 'Deliveries']
        
        fig = px.pie(
            vehicle_counts,
            values='Deliveries',
            names='Vehicle Type',
            title="Deliveries by Vehicle Type"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def create_last_mile_analysis(df):
    """
    Create pincode analysis for last mile data
    
    Args:
        df: pandas DataFrame with filtered data
    """
    if 'postcode' in df.columns:
        st.markdown("### Pincode Analysis")
        
        # Get top pincodes by delivery count
        pincode_counts = df['postcode'].value_counts().reset_index()
        pincode_counts.columns = ['Pincode', 'Deliveries']
        
        # If there are many pincodes, just show top 15
        if len(pincode_counts) > 15:
            display_pincodes = pincode_counts.head(15)
            show_more = st.checkbox("Show all pincodes", key="last_mile_pincodes")
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
