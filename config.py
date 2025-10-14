"""
Configuration file for KYC Document Extractor
Centralizes model definitions, pricing, and settings
"""

# Model configurations with pricing information
MODEL_OPTIONS = {
    "🔬 Qwen (Accurate)": {
        "id": "accounts/fireworks/models/qwen2p5-vl-32b-instruct",
        "name": "Qwen 2.5 VL 32B",
        "speed": "slow",
        "description": "Most accurate, slower processing",
        "input_cost_per_1m": 0.9,  # $0.9 per 1M input tokens
        "output_cost_per_1m": 0.9,  # $0.9 per 1M output tokens
    },
    "🎯 Llama Maverick (Balanced)": {
        "id": "accounts/fireworks/models/llama-v3p2-90b-vision-instruct",
        "name": "Llama 3.2 90B Vision Maverick",
        "speed": "medium",
        "description": "Balanced speed and accuracy",
        "input_cost_per_1m": 0.22,  # $0.22 per 1M input tokens
        "output_cost_per_1m": 0.88,  # $0.88 per 1M output tokens
    },
    "⚡ Llama Scout (Fast)": {
        "id": "accounts/fireworks/models/llama-v3p2-11b-vision-instruct",
        "name": "Llama 3.2 11B Vision Scout",
        "speed": "fast",
        "description": "Fastest, good for classification",
        "input_cost_per_1m": 0.15,  # $0.15 per 1M input tokens
        "output_cost_per_1m": 0.60,  # $0.60 per 1M output tokens
    },
}

# Default models
# Classification: Fast model (Maverick for balanced speed/accuracy)
# Extraction: Accurate model (Qwen for best results)
DEFAULT_CLASSIFICATION_MODEL = (
    "accounts/fireworks/models/llama-v3p2-90b-vision-instruct"  # Maverick
)
DEFAULT_EXTRACTION_MODEL = "accounts/fireworks/models/qwen2p5-vl-32b-instruct"  # Qwen


# Get pricing for a specific model ID
def get_model_pricing(model_id: str) -> dict:
    """
    Get pricing information for a model by its ID.
    Returns dict with input_cost_per_1m and output_cost_per_1m.
    """
    for model_info in MODEL_OPTIONS.values():
        if model_info["id"] == model_id:
            return {
                "input_cost_per_1m": model_info["input_cost_per_1m"],
                "output_cost_per_1m": model_info["output_cost_per_1m"],
            }

    # Default fallback if model not found
    return {"input_cost_per_1m": 0.9, "output_cost_per_1m": 0.9}


# Get model name by ID
def get_model_name(model_id: str) -> str:
    """Get display name for a model by its ID."""
    for key, model_info in MODEL_OPTIONS.items():
        if model_info["id"] == model_id:
            return key
    return "Unknown Model"
