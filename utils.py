import streamlit as st
import numpy as np
from datetime import datetime, timedelta

def set_page_config():
    """
    Set the page configuration for the Streamlit app
    """
    st.set_page_config(
        page_title="Blowhorn Network Analysis Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def generate_color_palette(items):
    """
    Generate a distinct color palette for a list of items
    
    Args:
        items: List of unique items to create colors for
        
    Returns:
        dict: Mapping of items to RGBA color values
    """
    colors = {}
    
    # Generate distinct colors for each item
    for i, item in enumerate(items):
        # Create colors with good separation (using HSL color space logic)
        hue = (i * 137.5) % 360  # Use golden angle to get good separation
        colors[item] = [
            int(255 * (0.7 + 0.3 * np.sin(np.radians(hue)))),  # R
            int(255 * (0.7 + 0.3 * np.sin(np.radians(hue + 120)))),  # G
            int(255 * (0.7 + 0.3 * np.sin(np.radians(hue + 240)))),  # B
            180  # Alpha
        ]
    
    return colors

def format_date_range(start_date, end_date):
    """
    Format date range for display
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        str: Formatted date range string
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    return f"{start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}"
