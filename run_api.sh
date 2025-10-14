#!/bin/bash
# Script to run the FastAPI server

echo "🚀 Starting KYC Document Extractor API..."
echo ""
echo "API will be available at:"
echo "  - Main API: http://localhost:8000"
echo "  - Docs (Swagger): http://localhost:8000/docs"
echo "  - Docs (ReDoc): http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Set API key if not already set (optional)
# export FIREWORKS_API_KEY="your-api-key"

# Run the API server
python api.py
