# Delivery Network Analysis Dashboard

A comprehensive interactive dashboard built with Streamlit to analyze delivery network operations. This application provides insights into delivery patterns, hub performance, vehicle utilization, and geographical distribution of deliveries.

![Dashboard Preview](https://via.placeholder.com/800x450?text=Delivery+Network+Analysis+Dashboard)

## Features

### Data Management
- **CSV Upload**: Upload your delivery data in CSV format
- **Sample Data**: Built-in sample data for demonstration
- **Download Template**: Get a sample template for your data

### Interactive Filtering
- **Date Range**: Filter data by specific timeframes
- **Hub Selection**: Focus on specific delivery hubs
- **Vehicle Types**: Filter by vehicle categories
- **Customers**: Analyze deliveries for specific customers

### Analysis Modules

#### Overview
- Key performance metrics
- Daily delivery trends
- Hub distribution analysis

#### Heatmaps
- Hub-Customer delivery patterns
- Vehicle type utilization by hub
- Average delivery distance by hub
- Package weight analysis

#### Geographic Analysis
- Interactive map with hub locations
- Delivery heatmap overlay
- Hub activity visualization

#### Driver Performance
- Top drivers by delivery count
- Driver efficiency metrics
- Distance per delivery analysis

#### Data Explorer
- Raw data viewing and exploration
- Statistical summaries
- Correlation analysis

## Data Format
Metabase Query: https://analytics.blowhorn.com/question/3109-network-analysis-order-heatmap?start=2025-04-09&end=2025-04-21
The application works best with CSV files that include the following fields:
- `number`: Unique identifier for each delivery
- `created_date`: Date and time of delivery creation
- `driver`: Name of the delivery driver
- `vehicle_model`: Type of vehicle used (e.g., Bike, Auto Rickshaw)
- `hub`: Dispatch location name
- `customer`: Customer/client name
- `postcode`: Delivery postal code
- `hub_long`: Hub longitude
- `hub_lat`: Hub latitude
- `delivered_long`: Delivery location longitude
- `delivered_lat`: Delivery location latitude
- `weight`: Package weight
- `kms`: Delivery distance in kilometers

## Installation and Setup

### Prerequisites
- Python 3.8 or higher

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/delivery-network-analysis.git
   cd delivery-network-analysis
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

Launch the Streamlit application:
```
streamlit run app.py
```

The application will open in your default web browser at http://localhost:8501.

## Usage Guide

1. **Upload Data**: Use the sidebar to upload your CSV file
2. **Apply Filters**: Select date ranges, hubs, vehicle types, or customers
3. **Explore Tabs**: Navigate through the different analysis modules
4. **Interact with Visualizations**: Hover, zoom, and click on charts for more information
5. **Export Insights**: Download visualizations using the built-in Streamlit export functionality

## Data Privacy

The application processes all data locally in your browser. No data is sent to external servers or stored beyond your session.

## Customization

You can customize the application by modifying the `app.py` file:
- Change color schemes by updating the Plotly color scales
- Add new analysis modules by creating additional tabs
- Customize metrics by modifying the calculations

## Troubleshooting

### Common Issues

**Problem**: CSV file won't upload  
**Solution**: Ensure your CSV follows the required format with header names matching the expected fields

**Problem**: Maps not displaying  
**Solution**: Check that your data contains valid latitude and longitude coordinates

**Problem**: Visualization errors  
**Solution**: Verify that your numeric data is properly formatted and contains no unexpected values

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Visualization powered by [Plotly](https://plotly.com/) and [Folium](https://python-visualization.github.io/folium/)
- Data analysis using [Pandas](https://pandas.pydata.org/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
