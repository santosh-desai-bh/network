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

def format_currency(value):
    """
    Format a number as Indian currency (with commas)
    
    Args:
        value: Numeric value to format
        
    Returns:
        str: Formatted currency string
    """
    if pd.isna(value):
        return "N/A"
    
    try:
        # Format with Indian number system (lakhs, crores)
        if value >= 10000000:  # Crore
            return f"₹{value/10000000:.2f} Cr"
        elif value >= 100000:  # Lakh
            return f"₹{value/100000:.2f} L"
        else:
            # For smaller values, use comma formatting
            return f"₹{value:,.2f}"
    except:
        return str(value)

import pandas as pd
def clean_numeric_string(s):
    """
    Clean a string containing a number (with commas, currency symbols etc.)
    and convert to float
    
    Args:
        s: String to clean
        
    Returns:
        float: Numeric value
    """
    if pd.isna(s) or s == '':
        return np.nan
    
    try:
        # If it's already a number, return it
        if isinstance(s, (int, float)):
            return float(s)
        
        # Remove currency symbols, commas, and other non-numeric characters
        # Keep decimal points and minus signs
        clean_str = ''.join(c for c in str(s) if c.isdigit() or c in ['.', '-'])
        return float(clean_str)
    except:
        return np.nan
