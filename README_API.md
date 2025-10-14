# KYC Document Extractor - REST API

A FastAPI-based REST API for programmatic access to the KYC document extraction service.

## Features

- 🚀 Fast, async API built with FastAPI
- 📝 Automatic OpenAPI documentation (Swagger UI)
- 🔒 CORS-enabled for web integration
- 💰 Cost tracking for each extraction
- ✅ Validation tests included
- 🎯 Multiple model options

## Installation

```bash
pip install -r requirements.txt
```

## Running the API

### Option 1: Using the script
```bash
./run_api.sh
```

### Option 2: Direct command
```bash
python api.py
```

### Option 3: Custom port
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs (interactive documentation)
- **ReDoc**: http://localhost:8000/redoc (alternative documentation)

## Endpoints

### `GET /`
Root endpoint with API information.

### `GET /health`
Health check endpoint.

### `GET /models`
Get information about available models.

### `POST /extract`
**Main endpoint** - Extract information from a document.

**Parameters:**
- `file` (required): Image file (JPG, PNG, etc.)
- `classification_model` (optional): Model for classification (default: Qwen 32B)
- `extraction_model` (optional): Model for extraction (default: Qwen 32B)
- `run_validations` (optional): Run validation tests (default: true)
- `api_key` (optional): Fireworks API key (uses environment variable if not provided)

**Response:**
```json
{
  "status": "success",
  "document_type": "passport",
  "classification_confidence": 0.95,
  "essential_fields": {
    "full_name": {"value": "JOHN DOE", "confidence": 1.0},
    "date_of_birth": {"value": "1990-01-15", "confidence": 1.0},
    "sex": {"value": "M", "confidence": 1.0},
    "address": {"value": "123 Main St", "confidence": 0.95}
  },
  "age": 35,
  "metadata": { ... },
  "_validation_results": { ... },
  "_cost_info": {
    "total_cost": 0.001234,
    "classification_cost": 0.000123,
    "extraction_cost": 0.001111,
    "currency": "USD",
    "usage_stats": { ... }
  }
}
```

### `POST /extract-simple`
Simplified endpoint with default parameters.

## Usage Examples

### cURL

```bash
# Basic extraction
curl -X POST "http://localhost:8000/extract" \
  -F "file=@/path/to/passport.jpg"

# With custom models
curl -X POST "http://localhost:8000/extract" \
  -F "file=@/path/to/license.jpg" \
  -F "classification_model=accounts/fireworks/models/qwen2p5-vl-32b-instruct" \
  -F "extraction_model=accounts/fireworks/models/llama-v3p2-90b-vision-instruct"
```

### Python

```python
import requests

# Basic extraction
with open("passport.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/extract",
        files={"file": f}
    )
    result = response.json()
    print(f"Name: {result['essential_fields']['full_name']['value']}")
    print(f"Cost: ${result['_cost_info']['total_cost']:.6f}")

# With custom parameters
with open("license.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/extract",
        files={"file": f},
        data={
            "classification_model": "accounts/fireworks/models/qwen2p5-vl-32b-instruct",
            "extraction_model": "accounts/fireworks/models/llama-v3p2-90b-vision-instruct",
            "run_validations": True
        }
    )
```

### JavaScript (fetch)

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/extract', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Extracted:', result);
```

### Python requests (detailed example)

```python
import requests
import json

def extract_document(image_path, api_key=None):
    """Extract information from a document."""

    url = "http://localhost:8000/extract"

    # Prepare the file
    with open(image_path, "rb") as f:
        files = {"file": f}

        # Optional parameters
        data = {
            "run_validations": True
        }

        if api_key:
            data["api_key"] = api_key

        # Make request
        response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        result = response.json()

        # Access results
        print(f"Document Type: {result['document_type']}")
        print(f"Name: {result['essential_fields']['full_name']['value']}")
        print(f"DOB: {result['essential_fields']['date_of_birth']['value']}")
        print(f"Total Cost: ${result['_cost_info']['total_cost']:.6f}")

        # Check validation
        validation = result['_validation_results']
        print(f"Validation: {validation['passed']}/{validation['total_tests']} passed")

        if validation['errors'] > 0:
            print("Errors found:")
            for error in validation['error_details']:
                print(f"  - {error['message']}")

        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Usage
result = extract_document("passport.jpg")
```

## Available Models

| Speed | Model ID | Description |
|-------|----------|-------------|
| ⚡ Fast | `accounts/fireworks/models/qwen2p5-vl-32b-instruct` | Quick processing, good accuracy |
| 🎯 Balanced | `accounts/fireworks/models/qwen2p5-vl-32b-instruct` | Best balance (default) |
| 🔬 Accurate | `accounts/fireworks/models/llama-v3p2-90b-vision-instruct` | Slower but highest accuracy |

## Environment Variables

```bash
# Optional: Set Fireworks API key
export FIREWORKS_API_KEY="your-api-key"

# Optional: Set custom port
export PORT=8000
```

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid file type, missing API key)
- `500`: Server error (extraction failed)

Example error response:
```json
{
  "detail": "Extraction failed: Invalid document format"
}
```

## Integration with Streamlit

The Streamlit UI uses the same `KYCDocumentExtractor` class directly, but you can modify it to call the API instead:

```python
# In streamlit_app.py, replace direct extraction with API call
import requests

def process_document_via_api(file, classification_model, extraction_model):
    files = {"file": file}
    data = {
        "classification_model": classification_model,
        "extraction_model": extraction_model
    }
    response = requests.post("http://localhost:8000/extract", files=files, data=data)
    return response.json()
```

## Deployment

### Docker (example)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment
The API can be deployed to:
- AWS Lambda (with Mangum adapter)
- Google Cloud Run
- Azure App Service
- Heroku
- DigitalOcean App Platform

## Security Notes

- In production, set specific CORS origins instead of `*`
- Use HTTPS in production
- Consider rate limiting
- Store API keys securely (environment variables, secrets manager)
- Validate file sizes and types

## Performance

- Async/await for non-blocking I/O
- Temporary file cleanup
- Supports concurrent requests
- Token usage tracking
- Cost calculation per request

## Support

For issues or questions:
- Check the interactive docs at `/docs`
- Review the examples above
- Check the main README.md
