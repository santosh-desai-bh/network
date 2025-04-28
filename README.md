# Blowhorn Network Analysis Dashboard

This application provides comprehensive visualization and analysis tools for Blowhorn's network operations, covering both first mile pickups and last mile deliveries.

## Features

### First Mile Analysis
- Interactive map visualization with heatmap of pickup locations
- Filtering by microwarehouse, customer, and hub
- Statistical analysis of pickup distances and order counts
- Relationship analysis between hubs and microwarehouses

### Last Mile Analysis
- Interactive map visualization with heatmap of delivery locations
- Filtering by hub, pincode, vehicle type, and customer
- Statistical analysis of delivery distances and service areas
- Pincode-based coverage analysis

## File Structure

- **app.py**: Main application entry point with tabbed interface
- **data_loader.py**: Functions for loading and preprocessing both types of data
- **data_filters.py**: UI components for filtering data in both analyses
- **map_visualization.py**: Map rendering for both first mile and last mile
- **analytics.py**: Statistical analysis and chart generation for both analyses
- **utils.py**: Utility functions shared across the application
- **requirements.txt**: Dependencies list

## Setup and Usage

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   streamlit run app.py
   ```

3. In the browser:
   - Choose between First Mile or Last Mile analysis tabs
   - Download CSV data from the analytics platform for the appropriate analysis
   - Upload the CSV file to the application
   - Use the filters in the sidebar to analyze specific data segments

## Data Requirements

### First Mile Data
The application expects a CSV file with the following columns:
- `trip_id`: Unique identifier for the pickup trip
- `customer`: Customer name
- `hub`: Hub identifier
- `customerlong`: Customer location longitude
- `customerlat`: Customer location latitude
- `pickedup_at`: Timestamp of pickup
- `microwarehouse`: Microwarehouse name
- `microwarehouselong`: Microwarehouse location longitude
- `microwarehouselat`: Microwarehouse location latitude
- `kms`: Distance in kilometers
- `num_orders`: Number of orders in the pickup

Additional columns like `start_time`, `end_time`, and `pickup_cutoff_limit` will be used if available.

### Last Mile Data
The application expects a CSV file with the following columns:
- `number`: Order number
- `created_date`: Order creation date
- `driver`: Driver name
- `vehicle_model`: Vehicle type
- `hub`: Hub identifier
- `customer`: Customer name
- `postcode`: Delivery pincode
- `hub_long`: Hub location longitude
- `hub_lat`: Hub location latitude
- `delivered_long`: Delivery location longitude
- `delivered_lat`: Delivery location latitude
- `kms`: Delivery distance in kilometers

Additional fields will be used if available.
