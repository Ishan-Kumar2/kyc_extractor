"""
Simple CLI example for KYC Document Extractor
For production use, consider using the API or Streamlit UI instead
"""

from model import KYCDocumentExtractor, print_extraction_summary
from config import DEFAULT_CLASSIFICATION_MODEL, DEFAULT_EXTRACTION_MODEL
import json
import os

if __name__ == "__main__":
    # Initialize extractor with default models
    api_key = os.environ.get("FIREWORKS_API_KEY", "fw_3ZdTBJnk2qnp1To57RM6KS8J")

    extractor = KYCDocumentExtractor(
        api_key=api_key,
        classification_model=DEFAULT_CLASSIFICATION_MODEL,  # Llama Maverick
        extraction_model=DEFAULT_EXTRACTION_MODEL,  # Qwen
    )

    # Example: Extract from an image
    image_path = "passport-1.jpeg"  # Update with your image path

    try:
        result = extractor.extract_document_info(image_path)

        # Print formatted summary
        print_extraction_summary(result)

        # Save result
        output_file = "extraction_result.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Full results saved to: {output_file}")

    except FileNotFoundError:
        print(f"\n✗ Error: Image file not found: {image_path}")
        print("Please update the 'image_path' variable with a valid image file.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
