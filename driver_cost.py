import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def load_driver_cost_data(file):
    """
    Load and preprocess driver cost data
    
    Args:
        file: Uploaded CSV file
        
    Returns:
        pandas DataFrame with preprocessed data
    """
    # Load the data
    df = pd.read_csv(file)
    
    # Convert string numbers with commas to float
    numeric_columns = ['total_cost', 'total_first_mile', 'total_mid_mile', 
                      'total_last_mile', 'total_orders', 'overall_cpo']
    
    for col in numeric_columns:
        if col in df.columns:
            # Replace empty strings with NaN
            df[col] = df[col].replace('', np.nan)
            # Handle string numbers with commas by removing commas and converting to float
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Process daily columns
    day_columns = [col for col in df.columns if any(col.startswith(prefix) for prefix in 
                  ['cost_day_', 'fm_day_', 'mm_day_', 'lm_day_', 'total_orders_day_', 'cpo_day_'])]
    
    for col in day_columns:
        if col in df.columns:
            # Replace empty strings with NaN
            df[col] = df[col].replace('', np.nan)
            # Handle string numbers with commas
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def create_driver_cost_filters(df):
    """
    Create sidebar filters for driver cost analysis
    
    Args:
        df: pandas DataFrame with driver cost data
        
    Returns:
        filtered DataFrame
    """
    with st.sidebar:
        st.header("Driver Cost Filters")
        
        # Create a copy of the dataframe to avoid modifying the original
        filtered_df = df.copy()
        
        # Display basic information
        st.markdown("## Data Summary")
        st.write(f"Total Drivers: {len(filtered_df)}")
        
        if 'total_cost' in filtered_df.columns:
            try:
                total_cost = filtered_df['total_cost'].sum()
                st.write(f"Total Cost: ₹{total_cost:,.2f}")
            except:
                st.write("Total Cost: N/A")
        
        # Filter by vehicle model
        if 'model_name' in filtered_df.columns:
            all_models = sorted(filtered_df['model_name'].unique().tolist())
            selected_models = st.multiselect(
                "Filter by Vehicle Model",
                options=all_models,
                default=all_models,
                key="driver_cost_vehicle_model"
            )
            
            if selected_models:
                filtered_df = filtered_df[filtered_df['model_name'].isin(selected_models)]
        
        # Filter by cost range
        if 'total_cost' in filtered_df.columns:
            min_cost = float(filtered_df['total_cost'].min())
            max_cost = float(filtered_df['total_cost'].max())
            
            cost_range = st.slider(
                "Filter by Cost Range (₹)",
                min_value=min_cost,
                max_value=max_cost,
                value=(min_cost, max_cost),
                key="driver_cost_range"
            )
            
            filtered_df = filtered_df[(filtered_df['total_cost'] >= cost_range[0]) & 
                                    (filtered_df['total_cost'] <= cost_range[1])]
        
        # Sort options
        sort_options = {
            "Driver Name (A-Z)": ("driver", False),
            "Driver Name (Z-A)": ("driver", True),
            "Total Cost (High to Low)": ("total_cost", True),
            "Total Cost (Low to High)": ("total_cost", False),
            "CPO (High to Low)": ("overall_cpo", True),
            "CPO (Low to High)": ("overall_cpo", False),
            "Total Orders (High to Low)": ("total_orders", True),
            "Total Orders (Low to High)": ("total_orders", False),
        }
        
        sort_by = st.selectbox(
            "Sort By",
            options=list(sort_options.keys()),
            key="driver_cost_sort"
        )
        
        sort_col, sort_asc = sort_options[sort_by]
        if sort_col in filtered_df.columns:
            try:
                filtered_df = filtered_df.sort_values(by=sort_col, ascending=not sort_asc)
            except:
                st.warning(f"Could not sort by {sort_by} due to missing or invalid data.")
    
    return filtered_df

def create_driver_cost_overview(df):
    """
    Create overview metrics and charts for driver cost analysis
    
    Args:
        df: pandas DataFrame with filtered driver cost data
    """
    st.markdown("### Driver Cost Overview")
    
    # Key metrics
    metrics_row = st.columns(4)
    
    with metrics_row[0]:
        total_drivers = len(df)
        st.metric("Total Drivers", f"{total_drivers}")
    
    with metrics_row[1]:
        if 'total_cost' in df.columns:
            try:
                total_cost = df['total_cost'].sum()
                st.metric("Total Cost", f"₹{total_cost:,.2f}")
            except:
                st.metric("Total Cost", "N/A")
    
    with metrics_row[2]:
        if 'total_orders' in df.columns:
            try:
                total_orders = df['total_orders'].sum()
                st.metric("Total Orders", f"{total_orders:,.0f}")
            except:
                st.metric("Total Orders", "N/A")
    
    with metrics_row[3]:
        if 'total_cost' in df.columns and 'total_orders' in df.columns:
            try:
                avg_cpo = df['total_cost'].sum() / df['total_orders'].sum()
                st.metric("Average CPO", f"₹{avg_cpo:.2f}")
            except:
                st.metric("Average CPO", "N/A")
    
    # Vehicle model distribution
    if 'model_name' in df.columns:
        st.markdown("### Vehicle Model Distribution")
        
        model_counts = df.groupby('model_name').size().reset_index()
        model_counts.columns = ['Vehicle Model', 'Count']
        
        model_costs = df.groupby('model_name')['total_cost'].sum().reset_index()
        model_costs.columns = ['Vehicle Model', 'Total Cost']
        
        # Merge the counts and costs
        model_data = pd.merge(model_counts, model_costs, on='Vehicle Model')
        model_data['Avg Cost per Vehicle'] = model_data['Total Cost'] / model_data['Count']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                model_data,
                values='Count',
                names='Vehicle Model',
                title="Distribution of Vehicle Models",
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                model_data,
                x='Vehicle Model',
                y='Avg Cost per Vehicle',
                title="Average Cost by Vehicle Model",
                color='Total Cost',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(xaxis_title="Vehicle Model", yaxis_title="Average Cost (₹)")
            st.plotly_chart(fig, use_container_width=True)
    
    # Top drivers by cost
    if 'driver' in df.columns and 'total_cost' in df.columns:
        st.markdown("### Top Drivers by Cost")
        
        # Get top 15 drivers by cost
        top_drivers = df.sort_values('total_cost', ascending=False).head(15)
        
        fig = px.bar(
            top_drivers,
            x='driver',
            y='total_cost',
            title="Top 15 Drivers by Total Cost",
            color='model_name' if 'model_name' in top_drivers.columns else None,
            labels={"driver": "Driver", "total_cost": "Total Cost (₹)", "model_name": "Vehicle Model"}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def create_cost_breakdown_analysis(df):
    """
    Create visualizations for cost breakdown analysis
    
    Args:
        df: pandas DataFrame with filtered driver cost data
    """
    st.markdown("### Cost Breakdown Analysis")
    
    if all(col in df.columns for col in ['total_first_mile', 'total_mid_mile', 'total_last_mile']):
        # Calculate aggregated costs
        total_fm = df['total_first_mile'].sum()
        total_mm = df['total_mid_mile'].sum()
        total_lm = df['total_last_mile'].sum()
        
        # Create data for pie chart
        cost_breakdown = pd.DataFrame({
            'Cost Type': ['First Mile', 'Mid Mile', 'Last Mile'],
            'Cost': [total_fm, total_mm, total_lm]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of cost breakdown
            fig = px.pie(
                cost_breakdown,
                values='Cost',
                names='Cost Type',
                title="Cost Distribution by Mile Type",
                color='Cost Type',
                color_discrete_map={
                    'First Mile': '#1f77b4',
                    'Mid Mile': '#ff7f0e',
                    'Last Mile': '#2ca02c'
                }
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bar chart comparing vehicle models by cost types
            if 'model_name' in df.columns:
                model_costs = df.groupby('model_name').agg({
                    'total_first_mile': 'sum',
                    'total_mid_mile': 'sum',
                    'total_last_mile': 'sum'
                }).reset_index()
                
                # Melt the dataframe for easier plotting
                model_costs_melted = pd.melt(
                    model_costs,
                    id_vars=['model_name'],
                    value_vars=['total_first_mile', 'total_mid_mile', 'total_last_mile'],
                    var_name='Cost Type',
                    value_name='Cost'
                )
                
                # Clean up the cost type names
                model_costs_melted['Cost Type'] = model_costs_melted['Cost Type'].map({
                    'total_first_mile': 'First Mile',
                    'total_mid_mile': 'Mid Mile',
                    'total_last_mile': 'Last Mile'
                })
                
                fig = px.bar(
                    model_costs_melted,
                    x='model_name',
                    y='Cost',
                    color='Cost Type',
                    title="Cost Breakdown by Vehicle Model",
                    barmode='group',
                    labels={"model_name": "Vehicle Model", "Cost": "Cost (₹)"}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
    
    # CPO Analysis
    if 'overall_cpo' in df.columns and 'model_name' in df.columns:
        st.markdown("### Cost Per Order (CPO) Analysis")
        
        # CPO by vehicle model
        cpo_by_model = df.groupby('model_name').agg({
            'overall_cpo': 'mean',
            'total_orders': 'sum'
        }).reset_index()
        
        cpo_by_model = cpo_by_model[cpo_by_model['total_orders'] > 0]  # Filter out models with no orders
        cpo_by_model.columns = ['Vehicle Model', 'Average CPO', 'Total Orders']
        
        fig = px.scatter(
            cpo_by_model,
            x='Average CPO',
            y='Total Orders',
            size='Total Orders',
            color='Vehicle Model',
            hover_name='Vehicle Model',
            title="CPO vs Orders by Vehicle Model",
            labels={"Average CPO": "Average Cost per Order (₹)"}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

def create_daily_trends_analysis(df):
    """
    Create visualizations for daily cost trends
    
    Args:
        df: pandas DataFrame with filtered driver cost data
    """
    st.markdown("### Daily Cost Trends Analysis")
    
    # Identify day columns
    day_cost_cols = [col for col in df.columns if col.startswith('cost_day_')]
    day_orders_cols = [col for col in df.columns if col.startswith('total_orders_day_')]
    day_cpo_cols = [col for col in df.columns if col.startswith('cpo_day_')]
    
    if day_cost_cols and day_orders_cols:
        # Aggregate daily costs and orders across all drivers
        daily_data = []
        
        for i in range(1, 32):  # Assuming up to 31 days
            cost_col = f'cost_day_{i}'
            orders_col = f'total_orders_day_{i}'
            cpo_col = f'cpo_day_{i}'
            
            if cost_col in df.columns and orders_col in df.columns:
                daily_cost = df[cost_col].sum()
                daily_orders = df[orders_col].sum()
                
                # Calculate daily CPO
                if daily_orders > 0:
                    daily_cpo = daily_cost / daily_orders
                else:
                    daily_cpo = 0
                
                daily_data.append({
                    'Day': i,
                    'Total Cost': daily_cost,
                    'Total Orders': daily_orders,
                    'CPO': daily_cpo
                })
        
        daily_df = pd.DataFrame(daily_data)
        
        # Create a line chart for daily costs and orders
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_df['Day'],
            y=daily_df['Total Cost'],
            mode='lines+markers',
            name='Total Cost',
            line=dict(color='#1f77b4', width=3),
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_df['Day'],
            y=daily_df['Total Orders'],
            mode='lines+markers',
            name='Total Orders',
            line=dict(color='#ff7f0e', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Daily Cost and Order Trends',
            xaxis=dict(
                title='Day',
                tickmode='linear',
                tick0=1,
                dtick=1
            ),
            yaxis=dict(
                title='Total Cost (₹)',
                titlefont=dict(color='#1f77b4'),
                tickfont=dict(color='#1f77b4')
            ),
            yaxis2=dict(
                title='Total Orders',
                titlefont=dict(color='#ff7f0e'),
                tickfont=dict(color='#ff7f0e'),
                anchor='x',
                overlaying='y',
                side='right'
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a bar chart for daily CPO
        fig = px.bar(
            daily_df,
            x='Day',
            y='CPO',
            title='Daily Cost Per Order (CPO)',
            labels={'CPO': 'Cost Per Order (₹)'},
            color='CPO',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
        st.plotly_chart(fig, use_container_width=True)

def create_detailed_driver_table(df):
    """
    Create a detailed table of driver cost data
    
    Args:
        df: pandas DataFrame with filtered driver cost data
    """
    st.markdown("### Detailed Driver Cost Data")
    
    # Create a copy of the dataframe with selected columns
    display_columns = [
        'driver', 'model_name', 'total_cost', 'total_first_mile', 
        'total_mid_mile', 'total_last_mile', 'total_orders', 'overall_cpo'
    ]
    
    display_df = df[display_columns].copy()
    
    # Rename columns for better display
    column_names = {
        'driver': 'Driver',
        'model_name': 'Vehicle Model',
        'total_cost': 'Total Cost (₹)',
        'total_first_mile': 'First Mile Cost (₹)',
        'total_mid_mile': 'Mid Mile Cost (₹)',
        'total_last_mile': 'Last Mile Cost (₹)',
        'total_orders': 'Total Orders',
        'overall_cpo': 'Cost Per Order (₹)'
    }
    
    display_df.rename(columns=column_names, inplace=True)
    
    # Format numeric columns
    for col in ['Total Cost (₹)', 'First Mile Cost (₹)', 'Mid Mile Cost (₹)', 'Last Mile Cost (₹)', 'Cost Per Order (₹)']:
        if col in display_df.columns:
            try:
                display_df[col] = display_df[col].map(lambda x: f"{x:,.2f}" if pd.notnull(x) else "N/A")
            except:
                pass
    
    st.dataframe(display_df, use_container_width=True)
