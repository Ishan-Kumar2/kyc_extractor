"""
Test script for the KYC Document Extractor API
Demonstrates how to use the API programmatically
"""

import requests
import json
import sys


def test_api_health():
    """Test if the API is running."""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API is healthy:", response.json())
            return True
        else:
            print("❌ API health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print(
            "❌ Cannot connect to API. Make sure it's running on http://localhost:8000"
        )
        print("   Run: python api.py")
        return False


def test_extract_document(image_path: str):
    """Test document extraction."""
    print(f"\n📄 Testing extraction for: {image_path}")

    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {
                "run_validations": True,
                "classification_model": "accounts/fireworks/models/qwen2p5-vl-32b-instruct",
                "extraction_model": "accounts/fireworks/models/qwen2p5-vl-32b-instruct",
            }

            print("⏳ Sending request...")
            response = requests.post(
                "http://localhost:8000/extract", files=files, data=data
            )

        if response.status_code == 200:
            result = response.json()

            print("\n✅ Extraction successful!")
            print("=" * 60)

            # Document type
            print(f"📋 Document Type: {result.get('document_type', 'N/A')}")
            print(f"   Confidence: {result.get('classification_confidence', 0):.0%}")

            # Essential fields
            print("\n👤 Essential Fields:")
            essential = result.get("essential_fields", {})

            if "full_name" in essential:
                print(f"   Name: {essential['full_name'].get('value', 'N/A')}")

            if "date_of_birth" in essential:
                print(f"   DOB: {essential['date_of_birth'].get('value', 'N/A')}")
                if "age" in result:
                    print(f"   Age: {result['age']} years")

            if "sex" in essential:
                print(f"   Sex: {essential['sex'].get('value', 'N/A')}")

            if "address" in essential:
                addr = essential["address"].get("value", "N/A")
                if addr != "N/A":
                    print(f"   Address: {addr}")

            # Validation results
            if "_validation_results" in result:
                validation = result["_validation_results"]
                print(
                    f"\n✅ Validation: {validation['passed']}/{validation['total_tests']} tests passed"
                )

                if validation["errors"] > 0:
                    print(f"   ❌ {validation['errors']} error(s):")
                    for error in validation["error_details"][:3]:  # Show first 3
                        print(f"      - {error['message']}")

                if validation["warnings"] > 0:
                    print(f"   ⚠️  {validation['warnings']} warning(s)")

            # Cost information
            if "_cost_info" in result:
                cost = result["_cost_info"]
                print(f"\n💰 Cost Information:")
                print(f"   Total: ${cost['total_cost']:.6f} USD")
                print(f"   Classification: ${cost['classification_cost']:.6f}")
                print(f"   Extraction: ${cost['extraction_cost']:.6f}")
                print(f"   Total Tokens: {cost['usage_stats']['total_tokens']:,}")

            print("=" * 60)

            # Save full result to JSON
            output_file = "api_test_result.json"
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Full result saved to: {output_file}")

            return result

        else:
            print(f"❌ Extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None

    except FileNotFoundError:
        print(f"❌ File not found: {image_path}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_get_models():
    """Test the models endpoint."""
    print("\n🔧 Available Models:")
    try:
        response = requests.get("http://localhost:8000/models")
        if response.status_code == 200:
            models = response.json()
            for key, model in models["models"].items():
                print(f"   {key.upper()}: {model['name']}")
                print(f"      Speed: {model['speed']} | {model['description']}")
            return True
        else:
            print("❌ Could not fetch models")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 KYC Document Extractor API Test")
    print("=" * 60)

    # Check if API is running
    if not test_api_health():
        sys.exit(1)

    # Get available models
    test_get_models()

    # Test extraction
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Try default test image
        import os

        possible_paths = [
            "passport-1.jpeg",
            "/Users/ishankumar/Desktop/Fall25/FireworksTakehome/passport-1.jpeg",
        ]

        image_path = None
        for path in possible_paths:
            if os.path.exists(path):
                image_path = path
                break

        if not image_path:
            print("\n⚠️  No test image provided")
            print("Usage: python test_api.py <path-to-image>")
            print("Example: python test_api.py passport-1.jpeg")
            sys.exit(0)

    result = test_extract_document(image_path)

    if result:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
