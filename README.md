# 🔍 KYC Document Extractor

AI-powered identity document processing system with web UI and REST API.

## Overview

Extract structured information from identity documents (passports, driver's licenses, state IDs, etc.) using vision-language models from Fireworks AI.



### Key Features

- ✅ **Multiple Document Types**: Passports, driver's licenses, state IDs, college IDs
- 🎯 **High Accuracy**: Confidence scores for each extracted field
- ✅ **Validation Tests**: 20+ sanity checks for data integrity
- 💰 **Cost Tracking**: Real-time token usage and cost calculation
- 🎨 **Web UI**: Clean Streamlit interface with confidence-based coloring
- 🚀 **REST API**: FastAPI endpoint for programmatic access
- 📊 **Comprehensive Output**: Essential fields + document-specific metadata

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (optional, can be hardcoded)
export FIREWORKS_API_KEY="your-api-key"
```

### Usage Options

#### 1. Streamlit Web UI (Recommended)
```bash
./run_streamlit.sh
# OR
streamlit run streamlit_app.py
```

Visit http://localhost:8501

#### 2. REST API
```bash
./run_api.sh
# OR
python api.py
```

Visit http://localhost:8000/docs for interactive API documentation

#### 3. Python Code
```python
from model import KYCDocumentExtractor

extractor = KYCDocumentExtractor(api_key="your-key")
result = extractor.extract_document_info("passport.jpg")

print(f"Name: {result['essential_fields']['full_name']['value']}")
print(f"Cost: ${result['_cost_info']['total_cost']:.6f}")
```

## Project Structure

```
FireworksTakehome/
├── model.py              # Core extraction logic
├── schemas.py            # JSON schemas (extendable)
├── validators.py         # Validation tests
├── prompts.py            # Extraction prompts
├── streamlit_app.py      # Web UI
├── api.py                # REST API
├── main.py               # CLI example
├── test_api.py           # API test script
├── requirements.txt      # Dependencies
└── README*.md            # Documentation
```

## Features in Detail

### 1. Document Types Supported

| Type | Essential Fields | Metadata |
|------|-----------------|----------|
| **Passport** | Name, DOB, Sex, Address | Passport #, Country, Dates, Nationality, Place of Birth |
| **Driver's License** | Name, DOB, Sex, Address | DL #, State, Dates, Height, Weight, Eye/Hair Color |
| **Other IDs** | Name, DOB, Sex, Address | ID #, Type, Issuing Authority, Dates |

### 2. Validation Tests

**Common Tests** (all documents):
- Name format validation
- Date of birth validity and reasonableness
- Age calculation (1-150 years)
- Sex value validation (M/F/X)

**Document-Specific Tests**:
- **Passports**: Number length, country validity, expiry checks
- **Licenses**: DL number, state validity, height/weight formats
- **Date Relationships**: Issue < Expiry, Issue > DOB, reasonable validity periods

### 3. Cost Tracking

Every extraction tracks:
- Prompt tokens (input cost)
- Completion tokens (output cost)
- Total cost per stage (classification + extraction)
- Grand total in USD

Example output:
```
💰 Total Cost: $0.001234 USD
   Classification: $0.000123 | Extraction: $0.001111
   Total Tokens: 5,432
```

### 4. Confidence-Based Display

Each field has a confidence score (0.0-1.0):
- **1.0 (Green)**: Crystal clear, no doubt
- **0.7-0.9 (Yellow-Green)**: Very clear, minor uncertainty
- **0.5-0.6 (Yellow)**: Readable but some ambiguity
- **0.0-0.4 (Red-Orange)**: Partially visible or unclear

The Streamlit UI uses continuous color gradients for visual confidence feedback.

### 5. Model Options

| Speed | Model | Description |
|-------|-------|-------------|
| ⚡ Fast | Llama 4 17B Vision Scout | Quick processing, good accuracy |
| 🎯 Balanced | Llama 4 17B Vision Maverick | Best balance (default) |
| 🔬 Accurate | Qwen 2.5 VL 32B | Slower but highest accuracy |

## API Usage

### REST API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Extract document
curl -X POST http://localhost:8000/extract \
  -F "file=@passport.jpg"

# Get available models
curl http://localhost:8000/models
```

### Python Client Example

```python
import requests

def extract_kyc(image_path):
    with open(image_path, "rb") as f:
        response = requests.post(
            "http://localhost:8000/extract",
            files={"file": f},
            data={"run_validations": True}
        )
    return response.json()

result = extract_kyc("passport.jpg")
print(f"Status: {result['status']}")
print(f"Document: {result['document_type']}")
print(f"Cost: ${result['_cost_info']['total_cost']:.6f}")
```

See [README_API.md](README_API.md) for detailed API documentation.

## Response Format

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
  "metadata": {
    "passport_number": {"value": "123456789", "confidence": 1.0},
    "country_of_issue": {"value": "USA", "confidence": 1.0},
    "date_of_issue": {"value": "2020-01-15", "confidence": 1.0},
    "date_of_expiry": {"value": "2030-01-15", "confidence": 1.0},
    "nationality": {"value": "USA", "confidence": 1.0},
    "place_of_birth": {"value": "New York, USA", "confidence": 1.0}
  },
  "extraction_notes": "All fields extracted with high confidence",
  "_validation_results": {
    "validation_run": true,
    "total_tests": 18,
    "passed": 18,
    "failed": 0,
    "errors": 0,
    "warnings": 0,
    "all_tests_passed": true
  },
  "_cost_info": {
    "total_cost": 0.001234,
    "classification_cost": 0.000123,
    "extraction_cost": 0.001111,
    "currency": "USD",
    "usage_stats": {
      "classification": {
        "prompt_tokens": 450,
        "completion_tokens": 50,
        "total_tokens": 500
      },
      "extraction": {
        "prompt_tokens": 1200,
        "completion_tokens": 300,
        "total_tokens": 1500
      },
      "total_tokens": 2000
    }
  }
}
```

## Architecture

### Schema System (schemas.py)

Extendable inheritance pattern:
- `get_essential_fields_schema()` - Base schema
- `get_passport_metadata_schema()` - Extends base
- `get_license_metadata_schema()` - Extends base
- `get_other_id_metadata_schema()` - Extends base

### Validation System (validators.py)

Document-specific validators:
- `DocumentValidator` class
- 20+ validation tests
- Severity levels (error vs warning)
- Detailed error messages

### Two-Stage Pipeline

1. **Classification** (fast model): Determine document type
2. **Extraction** (detailed model): Extract all fields with confidence scores

## Development

### Adding New Document Types

1. Add schema in `schemas.py`:
```python
def get_new_doc_metadata_schema():
    return {
        "type": "object",
        "properties": { ... }
    }
```

2. Add prompt in `prompts.py`:
```python
NEW_DOC_PROMPT = """Extract information from ..."""
```

3. Add extraction method in `model.py`:
```python
def extract_new_doc_info(self, base64_image):
    # Implementation
```

4. Add validator in `validators.py`:
```python
def _validate_new_doc(self, essential_fields, metadata):
    # Validation logic
```

### Testing

```bash
# Test API
python test_api.py passport-1.jpeg

# Test Streamlit (manual)
streamlit run streamlit_app.py

# Test CLI
python main.py
```

## Deployment

### Docker Example
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# For API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# OR for Streamlit
# CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501"]
```

### Environment Variables
```bash
FIREWORKS_API_KEY=your-api-key    # Required
PORT=8000                          # Optional for API
```

## Cost Optimization

- Use **Fast model** for classification (quick, cheap)
- Use **Balanced model** for extraction (default)
- Use **Accurate model** only when highest precision needed
- Typical cost per extraction: **$0.001 - $0.005 USD**

## Security Notes

- Validate file types and sizes
- Sanitize file uploads
- Use HTTPS in production
- Store API keys securely
- Set specific CORS origins in production
- Consider rate limiting

## Troubleshooting

### API Key Issues
```python
# Option 1: Environment variable
export FIREWORKS_API_KEY="your-key"

# Option 2: Pass directly
extractor = KYCDocumentExtractor(api_key="your-key")
```

### Import Errors
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Streamlit
streamlit run streamlit_app.py --server.port=8502

# API
uvicorn api:app --port=8001
```

## Documentation

- [README_STREAMLIT.md](README_STREAMLIT.md) - Web UI documentation
- [README_API.md](README_API.md) - REST API documentation
- `/docs` endpoint - Interactive API documentation (when API is running)

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests:
1. Check the documentation
2. Review the examples
3. Test with the provided scripts
4. Open an issue on GitHub

## Credits

Built with:
- [Fireworks AI](https://fireworks.ai/) - Vision-language models
- [FastAPI](https://fastapi.tiangolo.com/) - REST API framework
- [Streamlit](https://streamlit.io/) - Web UI framework
- [OpenAI Python SDK](https://github.com/openai/openai-python) - API client

---
