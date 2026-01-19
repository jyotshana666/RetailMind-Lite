#!/bin/bash
echo "🏪 RetailMind Lite - AI Demo"
echo "============================="

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Generate data if not exists
echo "📊 Generating retail data..."
python -c "from data.generate_data import generate_retail_dataset; generate_retail_dataset()"

# Run the application
echo "🚀 Starting RetailMind Lite..."
echo "🌐 Open http://localhost:8501 in your browser"
streamlit run app.py