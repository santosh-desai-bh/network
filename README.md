# Last Mile Delivery Analysis Streamlit App - Setup Guide

This guide walks you through setting up and running the Last Mile Delivery Analysis Streamlit application on your local machine.

## Prerequisites

- Python 3.7 or higher
- Pip package manager
- Your last mile delivery data in CSV format

## Step 1: Create a Project Directory

Create a new directory for your project and navigate into it:

```bash
mkdir last-mile-analysis
cd last-mile-analysis
```

## Step 2: Set Up a Virtual Environment (Recommended)

You can use either `venv` (built into Python) or `virtualenv` to create an isolated environment. Choose one of the following methods:

### Option 1: Using venv (Python built-in)

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### Option 2: Using virtualenv

First, install virtualenv if you don't have it already:
```bash
pip install virtualenv
```

Then create and activate a virtual environment:

#### On Windows:
```bash
virtualenv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
virtualenv venv
source venv/bin/activate
```

## Step 3: Install Required Packages

Create a file named `requirements.txt` with the following content:

```
streamlit==1.32.0
pandas==2.1.0
numpy==1.26.0
matplotlib==3.8.0
seaborn==0.13.0
scikit-learn==1.4.0
folium==0.15.0
streamlit-folium==0.15.0
plotly==5.18.0
haversine==2.8.0
```

Then install the requirements:

```bash
pip install -r requirements.txt
```

## Step 4: Create the Application File

Create a file named `app.py` and copy the provided Streamlit application code into it.

## Step 5: Prepare Your Data

Ensure your CSV file has the following columns:
- `number`: Delivery ID
- `created_date`: Date and time of delivery
- `driver`: Driver name
- `registration_certificate_number`: Vehicle registration
- `vehicle_model`: Type of vehicle
- `hub`: Delivery hub name
- `customer`: Customer name
- `postcode`: Delivery postcode
- `hub_long`: Hub longitude
- `hub_lat`: Hub latitude
- `delivered_long`: Delivery location longitude
- `delivered_lat`: Delivery location latitude
- `weight`: Package weight
- `kms`: Distance in kilometers

Place your CSV file in the project directory or be ready to upload it through the app.

## Step 6: Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

This will launch the app and open it in your default web browser. If it doesn't open automatically, you can access it at http://localhost:8501.

## Step 7: Upload Your Data

Once the app is running:
1. Use the file uploader in the sidebar to upload your CSV file
2. Alternatively, select "Use demo data" to explore the app with sample data

## Step 8: Explore the Dashboard

Navigate through the different sections using the sidebar:
- 📊 **Overview**: General statistics and distributions
- 🗺️ **Route Map**: Interactive maps of delivery routes
- 🔍 **Clustering Analysis**: Grouping of delivery locations
- 📈 **Delivery Insights**: Patterns by time, hub, and driver
- 📋 **Data Explorer**: Filter and analyze raw data
- 💡 **Optimization Suggestions**: Data-driven recommendations

## Troubleshooting

### Common Issues:

1. **Missing Dependencies**:
   ```bash
   pip install streamlit pandas numpy matplotlib seaborn scikit-learn folium streamlit-folium plotly haversine
   ```

2. **Map Rendering Issues**:
   - Ensure you have a stable internet connection
   - Try a different browser if maps don't render properly

3. **Performance Issues with Large Datasets**:
   - Consider filtering your data to a smaller subset for faster analysis
   - Increase your system's memory allocation to Python if possible

4. **CSV Format Issues**:
   - Ensure your CSV is properly formatted with the expected column names
   - Check for missing values in critical columns (coordinates, dates)

## Deployment Options

To share the app with your team:

1. **Local Network Deployment**:
   ```bash
   streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   ```
   Then others on your network can access it at http://YOUR_IP:8501

2. **Cloud Deployment**:
   - Consider deploying to Streamlit Cloud, Heroku, or AWS for wider access
   - Follow platform-specific deployment instructions

## Next Steps

- Customize the app code to match your specific business requirements
- Add additional analysis capabilities as needed
- Set up automated data pipelines for regular updates

For more information on customizing Streamlit apps, visit the [Streamlit documentation](https://docs.streamlit.io/).
