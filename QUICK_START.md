# KYC Document Extractor - Quick Start

## Installation
```bash
pip install -r requirements.txt
export FIREWORKS_API_KEY="your-api-key"  # Optional (has default)
```

## Usage

### Option 1: Web UI (Easiest)
```bash
./run_streamlit.sh
```
→ Opens http://localhost:8501

### Option 2: REST API
```bash
./run_api.sh
```
→ API: http://localhost:8000
→ Docs: http://localhost:8000/docs

### Option 3: Python
```python
from model import KYCDocumentExtractor

extractor = KYCDocumentExtractor()  # Uses smart defaults
result = extractor.extract_document_info("passport.jpg")

print(f"Name: {result['essential_fields']['full_name']['value']}")
print(f"Cost: ${result['_cost_info']['total_cost']:.6f}")
```

### Option 4: API Call
```python
import requests

with open("passport.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/extract",
        files={"file": f}
    )
print(response.json())
```

## Default Models

- **Classification**: Llama Maverick ($0.22/$0.88 per 1M tokens)
- **Extraction**: Qwen ($0.9/$0.9 per 1M tokens)

Change in config.py or pass as parameters.

## Features

✅ Passports, Licenses, State IDs, College IDs
✅ 20+ validation tests
✅ Cost tracking per extraction
✅ Confidence scores (0-1) for each field
✅ Web UI with color-coded confidence
✅ REST API with OpenAPI docs

## Files

- `config.py` - Models & pricing (⭐ edit here)
- `model.py` - Core extraction logic
- `streamlit_app.py` - Web UI
- `api.py` - REST API
- `main.py` - CLI example

## Testing

```bash
python test_api.py passport-1.jpeg
```

## Documentation

- [README.md](README.md) - Complete guide
- [SUBMISSION.md](SUBMISSION.md) - Submission summary
- [README_API.md](README_API.md) - API docs
- [README_STREAMLIT.md](README_STREAMLIT.md) - UI docs

## Support

Check `/docs` endpoint when API is running for interactive API documentation.
