import os
import base64
import json
from pathlib import Path
from typing import Optional, Dict, Any, Literal
from PIL import Image
import io
from datetime import datetime
from prompts import (
    CLASSIFICATION_PROMPT,
    PASSPORT_PROMPT,
    LICENSE_PROMPT,
    OTHER_ID_PROMPT,
)
from schemas import (
    get_classification_schema,
    get_extraction_schema_passport,
    get_extraction_schema_license,
    get_extraction_schema_other_id,
)
from validators import DocumentValidator
from config import (
    DEFAULT_CLASSIFICATION_MODEL,
    DEFAULT_EXTRACTION_MODEL,
    get_model_pricing,
)

try:
    from openai import OpenAI
except ImportError:
    print("Installing required package: openai")
    os.system("pip install openai pillow")
    from openai import OpenAI


class KYCDocumentExtractor:
    """
    Extract KYC information from identity documents using Fireworks AI.
    Two-stage process: Classification -> Extraction
    """

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

    def __init__(
        self,
        api_key: Optional[str] = None,
        classification_model: str = DEFAULT_CLASSIFICATION_MODEL,
        extraction_model: str = DEFAULT_EXTRACTION_MODEL,
        run_validations: bool = True,
    ):
        """
        Initialize the KYC extractor.

        Args:
            api_key: Fireworks API key
            classification_model: Model for document type classification
            extraction_model: Model for detailed extraction
            run_validations: Whether to run sanity check validations on extracted data
        """
        self.api_key = api_key or os.environ.get("FIREWORKS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Fireworks API key required. Set FIREWORKS_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = OpenAI(
            base_url="https://api.fireworks.ai/inference/v1", api_key=self.api_key
        )

        self.classification_model = classification_model
        self.extraction_model = extraction_model
        self.run_validations = run_validations

        # Initialize validator
        if self.run_validations:
            self.validator = DocumentValidator()

        # Track token usage and costs
        self.usage_stats = {
            "classification": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "extraction": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "total_tokens": 0,
        }

    def read_image(self, image_path: str) -> str:
        """Read an image file and convert to base64."""
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        try:
            with Image.open(image_path) as img:
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

                max_dimension = 2048
                if max(img.size) > max_dimension:
                    img.thumbnail(
                        (max_dimension, max_dimension), Image.Resampling.LANCZOS
                    )
                    print(f"Image resized to {img.size} for optimal processing")

                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=95)
                img_bytes = buffer.getvalue()

        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")

        base64_image = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/jpeg;base64,{base64_image}"

    def calculate_age(self, dob: str) -> Optional[int]:
        """Calculate age from date of birth (YYYY-MM-DD format)."""
        try:
            birth_date = datetime.strptime(dob, "%Y-%m-%d")
            today = datetime.now()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )
            return age
        except:
            return None

    def calculate_cost(self) -> Dict[str, Any]:
        """Calculate cost based on actual token usage and model-specific pricing."""

        # Get pricing for classification model
        class_pricing = get_model_pricing(self.classification_model)
        classification_cost = (
            self.usage_stats["classification"]["prompt_tokens"]
            * class_pricing["input_cost_per_1m"]
            / 1_000_000
        ) + (
            self.usage_stats["classification"]["completion_tokens"]
            * class_pricing["output_cost_per_1m"]
            / 1_000_000
        )

        # Get pricing for extraction model
        extract_pricing = get_model_pricing(self.extraction_model)
        extraction_cost = (
            self.usage_stats["extraction"]["prompt_tokens"]
            * extract_pricing["input_cost_per_1m"]
            / 1_000_000
        ) + (
            self.usage_stats["extraction"]["completion_tokens"]
            * extract_pricing["output_cost_per_1m"]
            / 1_000_000
        )

        total_cost = classification_cost + extraction_cost

        return {
            "classification_cost": classification_cost,
            "extraction_cost": extraction_cost,
            "total_cost": total_cost,
            "currency": "USD",
            "usage_stats": self.usage_stats,
            "models_used": {
                "classification": self.classification_model,
                "extraction": self.extraction_model,
            },
        }

    def get_classification_schema(self) -> Dict[str, Any]:
        """Schema for document type classification."""
        return get_classification_schema()

    def get_extraction_schema_passport(self) -> Dict[str, Any]:
        """Schema for passport extraction."""
        return get_extraction_schema_passport()

    def get_extraction_schema_license(self) -> Dict[str, Any]:
        """Schema for driver's license extraction."""
        return get_extraction_schema_license()

    def classify_document(self, base64_image: str) -> Dict[str, Any]:
        """
        Stage 1: Classify document type.

        Returns:
            Dictionary with document_type, confidence, and reasoning
        """
        prompt = CLASSIFICATION_PROMPT

        schema = self.get_classification_schema()

        print("Stage 1: Classifying document type...")

        try:
            response = self.client.chat.completions.create(
                model=self.classification_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": base64_image}},
                        ],
                    }
                ],
                response_format={"type": "json_object", "schema": schema},
                temperature=0.1,
                max_tokens=512,
            )

            # Track token usage
            if hasattr(response, "usage") and response.usage:
                self.usage_stats["classification"][
                    "prompt_tokens"
                ] = response.usage.prompt_tokens
                self.usage_stats["classification"][
                    "completion_tokens"
                ] = response.usage.completion_tokens
                self.usage_stats["classification"][
                    "total_tokens"
                ] = response.usage.total_tokens
                self.usage_stats["total_tokens"] += response.usage.total_tokens

            result = json.loads(response.choices[0].message.content)
            print(
                f"✓ Classification: {result['document_type']} (confidence: {result.get('confidence', 0):.2%})"
            )
            return result

        except Exception as e:
            print(f"✗ Classification failed: {e}")
            return {
                "document_type": "invalid",
                "confidence": 0.0,
                "reasoning": f"Classification error: {str(e)}",
            }

    def extract_passport_info(self, base64_image: str) -> Dict[str, Any]:
        """Stage 2: Extract passport information."""
        prompt = PASSPORT_PROMPT

        schema = self.get_extraction_schema_passport()

        print("Stage 2: Extracting passport details...")

        try:
            response = self.client.chat.completions.create(
                model=self.extraction_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": base64_image}},
                        ],
                    }
                ],
                response_format={"type": "json_object", "schema": schema},
                temperature=0.1,
                max_tokens=2048,
            )

            # Track token usage
            if hasattr(response, "usage") and response.usage:
                self.usage_stats["extraction"][
                    "prompt_tokens"
                ] += response.usage.prompt_tokens
                self.usage_stats["extraction"][
                    "completion_tokens"
                ] += response.usage.completion_tokens
                self.usage_stats["extraction"][
                    "total_tokens"
                ] += response.usage.total_tokens
                self.usage_stats["total_tokens"] += response.usage.total_tokens

            result = json.loads(response.choices[0].message.content)
            print("✓ Passport extraction completed")
            return result

        except Exception as e:
            print(f"✗ Extraction failed: {e}")
            raise

    def extract_license_info(self, base64_image: str) -> Dict[str, Any]:
        """Stage 2: Extract driver's license information."""
        prompt = LICENSE_PROMPT

        schema = self.get_extraction_schema_license()

        print("Stage 2: Extracting license details...")

        try:
            response = self.client.chat.completions.create(
                model=self.extraction_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": base64_image}},
                        ],
                    }
                ],
                response_format={"type": "json_object", "schema": schema},
                temperature=0.1,
                max_tokens=2048,
            )

            # Track token usage
            if hasattr(response, "usage") and response.usage:
                self.usage_stats["extraction"][
                    "prompt_tokens"
                ] += response.usage.prompt_tokens
                self.usage_stats["extraction"][
                    "completion_tokens"
                ] += response.usage.completion_tokens
                self.usage_stats["extraction"][
                    "total_tokens"
                ] += response.usage.total_tokens
                self.usage_stats["total_tokens"] += response.usage.total_tokens

            result = json.loads(response.choices[0].message.content)
            print("✓ License extraction completed")
            return result

        except Exception as e:
            print(f"✗ Extraction failed: {e}")
            raise

    def extract_other_id_info(self, base64_image: str) -> Dict[str, Any]:
        """Stage 2: Extract information from other ID types (state ID, college ID, etc.)."""
        prompt = OTHER_ID_PROMPT

        schema = get_extraction_schema_other_id()

        print("Stage 2: Extracting other ID details...")

        try:
            response = self.client.chat.completions.create(
                model=self.extraction_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": base64_image}},
                        ],
                    }
                ],
                response_format={"type": "json_object", "schema": schema},
                temperature=0.1,
                max_tokens=2048,
            )

            # Track token usage
            if hasattr(response, "usage") and response.usage:
                self.usage_stats["extraction"][
                    "prompt_tokens"
                ] += response.usage.prompt_tokens
                self.usage_stats["extraction"][
                    "completion_tokens"
                ] += response.usage.completion_tokens
                self.usage_stats["extraction"][
                    "total_tokens"
                ] += response.usage.total_tokens
                self.usage_stats["total_tokens"] += response.usage.total_tokens

            result = json.loads(response.choices[0].message.content)
            print("✓ Other ID extraction completed")
            return result

        except Exception as e:
            print(f"✗ Extraction failed: {e}")
            raise

    def extract_document_info(self, image_path: str) -> Dict[str, Any]:
        """
        Main extraction pipeline: Classify -> Extract

        Returns:
            Structured dictionary with essential_fields, metadata, and processing info
        """
        print(f"\n{'='*60}")
        print(f"Processing: {image_path}")
        print(f"{'='*60}")

        # Read image
        base64_image = self.read_image(image_path)

        # Stage 1: Classification
        classification = self.classify_document(base64_image)
        doc_type = classification["document_type"]

        if doc_type == "invalid":
            return {
                "status": "invalid",
                "classification": classification,
                "message": "Document could not be classified as passport or driver's license",
            }

        # Stage 2: Extraction based on document type
        try:
            if doc_type == "passport":
                extraction_result = self.extract_passport_info(base64_image)
                metadata_key = "passport_metadata"
            elif doc_type == "drivers_license":
                extraction_result = self.extract_license_info(base64_image)
                metadata_key = "license_metadata"
            elif doc_type == "other_id":
                extraction_result = self.extract_other_id_info(base64_image)
                metadata_key = "other_id_metadata"
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

            # Calculate age from DOB
            dob = (
                extraction_result.get("essential_fields", {})
                .get("date_of_birth", {})
                .get("value")
            )
            age = self.calculate_age(dob) if dob else None

            # Structure final result
            final_result = {
                "status": "success",
                "document_type": doc_type,
                "classification_confidence": classification.get("confidence"),
                "essential_fields": extraction_result.get("essential_fields", {}),
                "age": age,
                "metadata": extraction_result.get(metadata_key, {}),
                "extraction_notes": extraction_result.get("extraction_notes"),
                "_processing_info": {
                    "image_path": str(image_path),
                    "classification_model": self.classification_model,
                    "extraction_model": self.extraction_model,
                    "classification_reasoning": classification.get("reasoning"),
                },
            }

            # Run validation tests if enabled
            if self.run_validations:
                print("\nRunning validation tests...")
                validation_results = self.validator.validate(final_result)
                final_result["_validation_results"] = validation_results

                # Print validation summary
                if validation_results.get("validation_run"):
                    total = validation_results["total_tests"]
                    passed = validation_results["passed"]
                    errors = validation_results["errors"]
                    warnings = validation_results["warnings"]

                    print(f"✓ Validation complete: {passed}/{total} tests passed")
                    if errors > 0:
                        print(f"  ✗ {errors} error(s) found")
                    if warnings > 0:
                        print(f"  ⚠ {warnings} warning(s) found")

                    # Print error details
                    if errors > 0:
                        print("\n  Error details:")
                        for error in validation_results["error_details"]:
                            print(f"    - {error['test']}: {error['message']}")

            # Add cost information
            cost_info = self.calculate_cost()
            final_result["_cost_info"] = cost_info
            print(f"\n💰 Total Cost: ${cost_info['total_cost']:.6f} USD")
            print(
                f"   Classification: ${cost_info['classification_cost']:.6f} | Extraction: ${cost_info['extraction_cost']:.6f}"
            )
            print(f"   Total Tokens: {self.usage_stats['total_tokens']:,}")

            return final_result

        except Exception as e:
            return {
                "status": "error",
                "document_type": doc_type,
                "classification": classification,
                "error": str(e),
                "message": "Extraction failed after successful classification",
            }

    def extract_and_save(
        self, image_path: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract information and save to JSON file."""
        result = self.extract_document_info(image_path)

        if output_path is None:
            input_path = Path(image_path)
            output_path = input_path.parent / f"{input_path.stem}_extracted.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Results saved to: {output_path}")
        return result


def print_extraction_summary(result: Dict[str, Any]):
    """Pretty print extraction results."""
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)

    if result["status"] != "success":
        print(f"Status: {result['status'].upper()}")
        print(f"Message: {result.get('message', 'Unknown error')}")
        return

    print(f"Document Type: {result['document_type'].upper()}")
    print(
        f"Classification Confidence: {result.get('classification_confidence', 0):.1%}"
    )

    print("\n" + "-" * 60)
    print("ESSENTIAL FIELDS")
    print("-" * 60)

    essential = result.get("essential_fields", {})

    name = essential.get("full_name", {})
    print(f"Name: {name.get('value', 'N/A')}")
    if "confidence" in name:
        print(f"  └─ Confidence: {name['confidence']:.1%}")

    dob = essential.get("date_of_birth", {})
    print(f"Date of Birth: {dob.get('value', 'N/A')}")
    if "confidence" in dob:
        print(f"  └─ Confidence: {dob['confidence']:.1%}")

    if result.get("age"):
        print(f"Age: {result['age']} years")

    sex = essential.get("sex", {})
    print(f"Sex: {sex.get('value', 'N/A')}")
    if "confidence" in sex:
        print(f"  └─ Confidence: {sex['confidence']:.1%}")

    address = essential.get("address", {})
    if address:
        print(f"Address: {address.get('value', 'N/A')}")
        if "confidence" in address:
            print(f"  └─ Confidence: {address['confidence']:.1%}")

    print("\n" + "-" * 60)
    print(f"{result['document_type'].upper()} METADATA")
    print("-" * 60)

    metadata = result.get("metadata", {})
    for key, value in metadata.items():
        if isinstance(value, dict):
            field_name = key.replace("_", " ").title()
            print(f"{field_name}: {value.get('value', 'N/A')}")
            if "confidence" in value:
                print(f"  └─ Confidence: {value['confidence']:.1%}")

    if result.get("extraction_notes"):
        print("\n" + "-" * 60)
        print("EXTRACTION NOTES")
        print("-" * 60)
        print(result["extraction_notes"])

    # Print validation results if present
    if "_validation_results" in result:
        validation = result["_validation_results"]
        if validation.get("validation_run"):
            print("\n" + "-" * 60)
            print("VALIDATION RESULTS")
            print("-" * 60)
            print(f"Total Tests: {validation['total_tests']}")
            print(f"Passed: {validation['passed']}")
            print(f"Failed: {validation['failed']}")
            print(f"Errors: {validation['errors']}")
            print(f"Warnings: {validation['warnings']}")

            if validation["errors"] > 0:
                print("\nErrors:")
                for error in validation["error_details"]:
                    print(f"  ✗ {error['test']}: {error['message']}")

            if validation["warnings"] > 0:
                print("\nWarnings:")
                for warning in validation["warning_details"]:
                    print(f"  ⚠ {warning['test']}: {warning['message']}")
