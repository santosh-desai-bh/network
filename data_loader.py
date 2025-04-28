import pandas as pd
import numpy as np
from datetime import datetime

def load_data(file):
    """
    Load data from CSV file
    
    Args:
        file: Uploaded CSV file
        
    Returns:
        pandas DataFrame
    """
    df = pd.read_csv(file)
    return df

def detect_data_type(df):
    """
    Detect if the dataframe contains first mile or last mile data
    
    Args:
        df: pandas DataFrame with raw data
        
    Returns:
        string: 'first_mile' or 'last_mile'
    """
    # Check for first mile specific columns
    first_mile_indicators = ['customerlong', 'customerlat', 'microwarehouse', 'microwarehouselong', 'microwarehouselat', 'pickedup_at']
    first_mile_score = sum(1 for col in first_mile_indicators if col in df.columns)
    
    # Check for last mile specific columns
    last_mile_indicators = ['hub_long', 'hub_lat', 'delivered_long', 'delivered_lat', 'created_date', 'postcode']
    last_mile_score = sum(1 for col in last_mile_indicators if col in df.columns)
    
    # Determine the type based on the higher score
    if first_mile_score > last_mile_score:
        return "first_mile"
    else:
        return "last_mile"

def preprocess_data(df, data_type="first_mile"):
    """
    Preprocess the data for visualization
    
    Args:
        df: pandas DataFrame with raw data
        data_type: string indicating 'first_mile' or 'last_mile'
        
    Returns:
        pandas DataFrame with preprocessed data
    """
    if data_type == "first_mile":
        # Convert date column if it exists
        if 'pickedup_at' in df.columns:
            df['pickedup_at'] = pd.to_datetime(df['pickedup_at'])
        
        # Convert numeric columns from strings to floats
        numeric_columns = ['customerlong', 'customerlat', 'microwarehouselong', 'microwarehouselat', 'kms']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Drop rows with NaN values in coordinate columns to avoid map errors
        df = df.dropna(subset=['microwarehouselong', 'microwarehouselat', 'customerlong', 'customerlat'])
        
        # Create color mapping for microwarehouses
        if 'microwarehouse' in df.columns:
            unique_microwarehouses = df['microwarehouse'].unique()
            colors = {}
            
            # Generate distinct colors for each microwarehouse
            for i, microwarehouse in enumerate(unique_microwarehouses):
                # Create colors with good separation (using HSL color space logic)
                hue = (i * 137.5) % 360  # Use golden angle to get good separation
                colors[microwarehouse] = [
                    int(255 * (0.7 + 0.3 * np.sin(np.radians(hue)))),  # R
                    int(255 * (0.7 + 0.3 * np.sin(np.radians(hue + 120)))),  # G
                    int(255 * (0.7 + 0.3 * np.sin(np.radians(hue + 240)))),  # B
                    180  # Alpha
                ]
            
            # Add color column to dataframe
            df['color'] = df['microwarehouse'].map(lambda x: colors.get(x, [100, 100, 100, 180]))
        else:
            # Default color if no microwarehouse column
            df['color'] = [[100, 100, 100, 180]] * len(df)
    
    elif data_type == "last_mile":
        # Convert date column if it exists
        if 'created_date' in df.columns:
            df['created_date'] = pd.to_datetime(df['created_date'])
        
        # Convert numeric columns from strings to floats
        numeric_columns = ['hub_long', 'hub_lat', 'delivered_long', 'delivered_lat', 'kms']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
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
        
        # Convert postcode to string if it exists
        if 'postcode' in df.columns:
            df['postcode'] = df['postcode'].astype(str)
    
    return df
