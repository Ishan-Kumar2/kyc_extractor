"""
JSON schemas for KYC document extraction.
Uses an inheritance pattern where specific document types extend the base essential fields.
"""

from typing import Dict, Any


def get_base_field_schema() -> Dict[str, Any]:
    """Base schema for a field with value and confidence."""
    return {
        "type": "object",
        "properties": {
            "value": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        },
        "required": ["value"],
    }


def get_essential_fields_schema() -> Dict[str, Any]:
    """
    Base schema for essential fields common to all identity documents.
    This is the foundation that all document types inherit from.
    """
    return {
        "type": "object",
        "properties": {
            "full_name": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Full name as it appears",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["value"],
            },
            "date_of_birth": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "DOB in YYYY-MM-DD format",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["value"],
            },
            "sex": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "enum": ["M", "F", "X"],
                        "description": "Gender",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["value"],
            },
            "address": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Full address if available",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
        },
        "required": ["full_name", "date_of_birth", "sex"],
    }


def get_classification_schema() -> Dict[str, Any]:
    """Schema for document type classification."""
    return {
        "type": "object",
        "properties": {
            "document_type": {
                "type": "string",
                "enum": ["passport", "drivers_license", "other_id", "invalid"],
                "description": "Type of identity document",
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Confidence score for the classification",
            },
            "reasoning": {
                "type": "string",
                "description": "Brief explanation of classification decision",
            },
        },
        "required": ["document_type", "confidence"],
    }


def get_passport_metadata_schema() -> Dict[str, Any]:
    """Schema for passport-specific metadata fields."""
    return {
        "type": "object",
        "properties": {
            "passport_number": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["value"],
            },
            "country_of_issue": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["value"],
            },
            "date_of_issue": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Issue date in YYYY-MM-DD format",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["value"],
            },
            "date_of_expiry": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Expiry date in YYYY-MM-DD format",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["value"],
            },
            "nationality": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "place_of_birth": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
        },
        "required": [
            "passport_number",
            "country_of_issue",
            "date_of_issue",
            "date_of_expiry",
        ],
    }


def get_license_metadata_schema() -> Dict[str, Any]:
    """Schema for driver's license-specific metadata fields."""
    return {
        "type": "object",
        "properties": {
            "dl_number": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["value"],
            },
            "date_of_issue": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Issue date in YYYY-MM-DD format",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "date_of_expiry": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Expiry date in YYYY-MM-DD format",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "height": {
                "type": "object",
                "properties": {
                    "value": {"type": "string", "description": "Height with units"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "weight": {
                "type": "object",
                "properties": {
                    "value": {"type": "string", "description": "Weight with units"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "eye_color": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "hair_color": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "issuing_state": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "class": {
                "type": "object",
                "properties": {
                    "value": {"type": "string", "description": "License class/type"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "restrictions": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Any driving restrictions",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "endorsements": {
                "type": "object",
                "properties": {
                    "value": {"type": "string", "description": "License endorsements"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
        },
        "required": ["dl_number"],
    }


def get_other_id_metadata_schema() -> Dict[str, Any]:
    """
    Schema for other ID types (state IDs, college IDs, etc.).
    These have minimal required metadata since they vary greatly.
    """
    return {
        "type": "object",
        "properties": {
            "id_number": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Any identification number found",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "issuing_authority": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Organization/authority that issued the ID",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "date_of_issue": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Issue date in YYYY-MM-DD format",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "date_of_expiry": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Expiry date in YYYY-MM-DD format",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "id_type": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Type of ID (e.g., 'State ID', 'College ID', 'Employee ID')",
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
        },
        "required": [],  # No required fields since other IDs vary greatly
    }


def get_extraction_schema_passport() -> Dict[str, Any]:
    """
    Complete extraction schema for passports.
    Extends essential_fields with passport_metadata.
    """
    return {
        "type": "object",
        "properties": {
            "essential_fields": get_essential_fields_schema(),
            "passport_metadata": get_passport_metadata_schema(),
            "extraction_notes": {
                "type": "string",
                "description": "Any issues or notes about extraction quality",
            },
        },
        "required": ["essential_fields", "passport_metadata"],
    }


def get_extraction_schema_license() -> Dict[str, Any]:
    """
    Complete extraction schema for driver's licenses.
    Extends essential_fields with license_metadata.
    """
    # Override address to be required for licenses
    essential_fields = get_essential_fields_schema()
    essential_fields["properties"]["address"]["required"] = ["value"]
    essential_fields["required"].append("address")

    return {
        "type": "object",
        "properties": {
            "essential_fields": essential_fields,
            "license_metadata": get_license_metadata_schema(),
            "extraction_notes": {
                "type": "string",
                "description": "Any issues or notes about extraction quality",
            },
        },
        "required": ["essential_fields", "license_metadata"],
    }


def get_extraction_schema_other_id() -> Dict[str, Any]:
    """
    Complete extraction schema for other ID types.
    Extends essential_fields with other_id_metadata.
    Only essential fields are attempted; metadata is optional.
    """
    return {
        "type": "object",
        "properties": {
            "essential_fields": get_essential_fields_schema(),
            "other_id_metadata": get_other_id_metadata_schema(),
            "extraction_notes": {
                "type": "string",
                "description": "Any issues or notes about extraction quality",
            },
        },
        "required": ["essential_fields"],  # Only essential fields required
    }
