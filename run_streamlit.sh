#!/bin/bash
# Quick script to run the Streamlit KYC Extractor

echo "🚀 Starting KYC Document Extractor..."
echo ""
echo "The app will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

# Set API key if not already set (optional)
# export FIREWORKS_API_KEY="your-api-key"

# Run streamlit
streamlit run streamlit_app.py
