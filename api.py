"""
FastAPI REST API for KYC Document Extractor
Provides programmatic access to document extraction functionality
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from pathlib import Path
from typing import Optional
import uvicorn

from model import KYCDocumentExtractor
from config import MODEL_OPTIONS, DEFAULT_CLASSIFICATION_MODEL, DEFAULT_EXTRACTION_MODEL

# Initialize FastAPI app
app = FastAPI(
    title="KYC Document Extractor API",
    description="AI-powered identity document processing API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "KYC Document Extractor API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "POST /extract": "Extract information from an identity document",
            "GET /health": "Health check endpoint",
            "GET /docs": "Interactive API documentation",
            "GET /redoc": "Alternative API documentation",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "KYC Document Extractor API"}


@app.post("/extract")
async def extract_document(
    file: UploadFile = File(
        ..., description="Identity document image (JPG, PNG, etc.)"
    ),
    classification_model: Optional[str] = Form(
        DEFAULT_CLASSIFICATION_MODEL,
        description="Model for document classification (default: Llama Maverick)",
    ),
    extraction_model: Optional[str] = Form(
        DEFAULT_EXTRACTION_MODEL,
        description="Model for data extraction (default: Qwen)",
    ),
    run_validations: Optional[bool] = Form(
        True, description="Whether to run validation tests"
    ),
    api_key: Optional[str] = Form(
        None, description="Fireworks API key (optional if set in environment)"
    ),
):
    """
    Extract information from an identity document.

    Upload an image of a passport, driver's license, or other ID document,
    and receive extracted information with confidence scores.

    **Supported document types:**
    - Passports
    - Driver's Licenses
    - State IDs
    - College IDs
    - Other identity documents

    **Response includes:**
    - Essential fields (name, DOB, sex, address)
    - Document-specific metadata
    - Validation test results
    - Cost information
    - Confidence scores for each field
    """

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image file (JPG, PNG, etc.)",
        )

    # Save uploaded file temporarily
    try:
        suffix = Path(file.filename).suffix if file.filename else ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Get API key from form or environment
        fireworks_api_key = api_key or os.environ.get("FIREWORKS_API_KEY")
        if not fireworks_api_key:
            raise HTTPException(
                status_code=400,
                detail="Fireworks API key required. Provide via api_key parameter or FIREWORKS_API_KEY environment variable",
            )

        # Initialize extractor
        extractor = KYCDocumentExtractor(
            api_key=fireworks_api_key,
            classification_model=classification_model,
            extraction_model=extraction_model,
            run_validations=run_validations,
        )

        # Extract document info
        result = extractor.extract_document_info(tmp_path)

        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

        # Return result
        return JSONResponse(content=result)

    except Exception as e:
        # Clean up temp file on error
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)

        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.post("/extract-simple")
async def extract_document_simple(
    file: UploadFile = File(..., description="Identity document image")
):
    """
    Simplified extraction endpoint with default parameters.

    Uses default models: Llama Maverick for classification, Qwen for extraction.
    """
    return await extract_document(
        file=file,
        classification_model=DEFAULT_CLASSIFICATION_MODEL,
        extraction_model=DEFAULT_EXTRACTION_MODEL,
        run_validations=True,
        api_key=None,
    )


# Model configuration info endpoint
@app.get("/models")
async def get_available_models():
    """Get information about available models."""
    return {"models": MODEL_OPTIONS}


# Run the API server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True, log_level="info")
