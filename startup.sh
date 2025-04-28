#!/bin/bash

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Update pip
echo "Updating pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing required packages..."
pip install -r requirements.txt

# Start the Streamlit application
echo "Starting Blowhorn Network Analysis Dashboard..."
streamlit run app.py

# Keep the terminal window open if running on Windows
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "Press any key to exit..."
    read -n 1
fi
