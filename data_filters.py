import streamlit as st
import pandas as pd

def create_first_mile_filters(df):
    """
    Create sidebar filters for the first mile dashboard
    
    Args:
        df: pandas DataFrame with preprocessed data
        
    Returns:
        pandas DataFrame with filtered data
    """
    with st.sidebar:
        st.header("First Mile Filters")
        
        # Create a copy of the dataframe to avoid modifying the original
        filtered_df = df.copy()
        
        # Display basic information
        st.markdown("## Data Summary")
        st.write(f"Total Pickups: {len(filtered_df)}")
        
        if 'pickedup_at' in filtered_df.columns:
            st.write(f"Date Range: {filtered_df['pickedup_at'].min().date()} to {filtered_df['pickedup_at'].max().date()}")
        
        # Filter by microwarehouse
        if 'microwarehouse' in filtered_df.columns:
            all_microwarehouses = sorted(filtered_df['microwarehouse'].unique().tolist())
            selected_microwarehouses = st.multiselect(
                "Filter by Microwarehouse",
                options=all_microwarehouses,
                default=all_microwarehouses,
                key="first_mile_microwarehouse"
            )
            
            if selected_microwarehouses:
                filtered_df = filtered_df[filtered_df['microwarehouse'].isin(selected_microwarehouses)]
        
        # Filter by customer
        if 'customer' in filtered_df.columns:
            all_customers = sorted(filtered_df['customer'].unique().tolist())
            selected_customers = st.multiselect(
                "Filter by Customer",
                options=all_customers,
                default=all_customers,
                key="first_mile_customer"
            )
            
            if selected_customers:
                filtered_df = filtered_df[filtered_df['customer'].isin(selected_customers)]
        
        # Filter by hub
        if 'hub' in filtered_df.columns:
            # Get unique hub values
            all_hubs = sorted(filtered_df['hub'].unique().tolist())
            
            # Create a mapping of customer to hub for the information display
            hub_customer_map = filtered_df.groupby('hub')['customer'].unique().apply(lambda x: ', '.join(x)).reset_index()
            hub_customer_map.columns = ['Hub', 'Customers']
            
            # Create a selectbox for choosing hub
            all_hub_options = ["All"] + all_hubs
            selected_hub = st.selectbox(
                "Filter by Hub",
                options=all_hub_options,
                key="first_mile_hub"
            )
            
            if selected_hub != "All":
                filtered_df = filtered_df[filtered_df['hub'] == selected_hub]
                
                # Show hub details
                hub_details = hub_customer_map[hub_customer_map['Hub'] == selected_hub]
                if not hub_details.empty:
                    st.markdown(f"**Hub {selected_hub} serves:**")
                    st.write(hub_details['Customers'].iloc[0])
                
                # Count pickups for this hub
                pickup_count = len(filtered_df)
                st.markdown(f"**Number of pickups:** {pickup_count}")
                
                # Calculate average distance for this hub
                if 'kms' in filtered_df.columns:
                    try:
                        avg_dist = round(filtered_df['kms'].mean(), 2)
                        st.markdown(f"**Average pickup distance:** {avg_dist} km")
                    except:
                        pass
        
        # Map settings
        st.markdown("## Map Settings")
        use_clusters = st.toggle("Use Marker Clusters", value=False, key="first_mile_clusters")
        
        # Store the cluster preference as a session state
        st.session_state['first_mile_use_clusters'] = use_clusters
    
    return filtered_df

def create_last_mile_filters(df):
    """
    Create sidebar filters for the last mile dashboard
    
    Args:
        df: pandas DataFrame with preprocessed data
        
    Returns:
        pandas DataFrame with filtered data
    """
    with st.sidebar:
        st.header("Last Mile Filters")
        
        # Create a copy of the dataframe to avoid modifying the original
        filtered_df = df.copy()
        
        # Display basic information
        st.markdown("## Data Summary")
        st.write(f"Total Deliveries: {len(filtered_df)}")
        
        if 'created_date' in filtered_df.columns:
            st.write(f"Date Range: {filtered_df['created_date'].min().date()} to {filtered_df['created_date'].max().date()}")
        
        # Filter by hub if the column exists
        if 'hub' in filtered_df.columns:
            all_hubs = sorted(filtered_df['hub'].unique().tolist())
            selected_hubs = st.multiselect(
                "Filter by Hub",
                options=all_hubs,
                default=all_hubs,
                key="last_mile_hub"
            )
            
            if selected_hubs:
                filtered_df = filtered_df[filtered_df['hub'].isin(selected_hubs)]
        
        # Filter by pincode if the column exists
        if 'postcode' in filtered_df.columns:
            # Get unique pincodes with their respective hubs
            pincode_hub_map = filtered_df.groupby('postcode')['hub'].unique().apply(lambda x: ', '.join(x)).reset_index()
            pincode_hub_map.columns = ['Pincode', 'Serving Hubs']
            
            # Create a selectbox for choosing pincode
            all_pincodes = ["All"] + sorted(filtered_df['postcode'].unique().tolist())
            selected_pincode = st.selectbox(
                "Filter by Pincode",
                options=all_pincodes,
                key="last_mile_pincode"
            )
            
            if selected_pincode != "All":
                filtered_df = filtered_df[filtered_df['postcode'] == selected_pincode]
                # Show pincode details
                pincode_details = pincode_hub_map[pincode_hub_map['Pincode'] == selected_pincode]
                if not pincode_details.empty:
                    st.markdown(f"**Pincode {selected_pincode} is served by:**")
                    st.write(pincode_details['Serving Hubs'].iloc[0])
                
                # Count deliveries for this pincode
                delivery_count = len(filtered_df)
                st.markdown(f"**Number of deliveries:** {delivery_count}")
                
                # Calculate average distance for this pincode
                if 'kms' in filtered_df.columns:
                    try:
                        avg_dist = round(filtered_df['kms'].mean(), 2)
                        st.markdown(f"**Average delivery distance:** {avg_dist} km")
                    except:
                        pass
        
        # Filter by vehicle model if the column exists
        if 'vehicle_model' in filtered_df.columns:
            all_vehicles = sorted(filtered_df['vehicle_model'].unique().tolist())
            selected_vehicles = st.multiselect(
                "Filter by Vehicle Type",
                options=all_vehicles,
                default=all_vehicles,
                key="last_mile_vehicle"
            )
            
            if selected_vehicles:
                filtered_df = filtered_df[filtered_df['vehicle_model'].isin(selected_vehicles)]
                
        # Filter by customer if the column exists
        if 'customer' in filtered_df.columns:
            all_customers = sorted(filtered_df['customer'].unique().tolist())
            selected_customers = st.multiselect(
                "Filter by Customer",
                options=all_customers,
                default=all_customers,
                key="last_mile_customer"
            )
            
            if selected_customers:
                filtered_df = filtered_df[filtered_df['customer'].isin(selected_customers)]
        
        # Map settings
        st.markdown("## Map Settings")
        use_clusters = st.toggle("Use Marker Clusters", value=False, key="last_mile_clusters")
        
        # Store the cluster preference as a session state
        st.session_state['last_mile_use_clusters'] = use_clusters
    
    return filtered_df
