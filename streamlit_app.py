"""
Streamlit UI for KYC Document Extractor
Clean, professional interface for document processing
"""

import streamlit as st
import json
import tempfile
import os
from pathlib import Path
from model import KYCDocumentExtractor
import io
from PIL import Image
from config import MODEL_OPTIONS

# Page configuration
st.set_page_config(
    page_title="KYC Extractor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for clean design and confidence coloring
st.markdown(
    """
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    .field-container {
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .field-label {
        font-weight: 600;
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 0.25rem;
    }
    .field-value {
        font-size: 1.1rem;
        color: #000;
    }
    .confidence-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .log-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-family: monospace;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #155724;
    }
    .error-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #721c24;
    }
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #856404;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Model options imported from config.py


def get_confidence_color(confidence):
    """
    Generate RGB color based on confidence score.
    0.0 (red) -> 1.0 (green) as a continuous spectrum.
    """
    if confidence is None:
        return "#e0e0e0"

    # Ensure confidence is between 0 and 1
    confidence = max(0.0, min(1.0, confidence))

    # Red to Yellow to Green gradient
    if confidence < 0.5:
        # Red to Yellow (0.0 to 0.5)
        r = 255
        g = int(255 * (confidence * 2))
        b = 0
    else:
        # Yellow to Green (0.5 to 1.0)
        r = int(255 * (2 - confidence * 2))
        g = 255
        b = 0

    return f"rgb({r}, {g}, {b})"


def get_confidence_background(confidence):
    """Get background color with opacity for field display."""
    if confidence is None:
        return "#f8f9fa"

    color = get_confidence_color(confidence)
    # Extract RGB values and add alpha
    return color.replace("rgb(", "rgba(").replace(")", ", 0.15)")


def display_field(label, value, confidence=None, container_style=""):
    """Display a field with confidence-based coloring."""
    if value is None or value == "":
        value = "N/A"

    # Get colors based on confidence
    bg_color = get_confidence_background(confidence)
    border_color = get_confidence_color(confidence) if confidence else "#e0e0e0"

    confidence_badge = ""
    if confidence is not None:
        badge_color = get_confidence_color(confidence)
        confidence_badge = f'<span class="confidence-badge" style="background: {badge_color}; color: white;">{confidence:.0%}</span>'

    html = f"""
    <div class="field-container" style="background: {bg_color}; border-left-color: {border_color}; {container_style}">
        <div class="field-label">{label} {confidence_badge}</div>
        <div class="field-value">{value}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def main():
    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>🔍 KYC Document Extractor</h1>
        <p style="font-size: 1.1rem; margin: 0;">AI-Powered Identity Document Processing</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # File upload section
    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Upload Identity Document",
            type=["jpg", "jpeg", "png", "webp", "gif", "bmp"],
            help="Upload a passport, driver's license, or other ID document",
        )

    with col2:
        if uploaded_file:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Document", use_container_width=True)

    # Model selection
    st.markdown("### ⚙️ Model Configuration")

    col1, col2 = st.columns(2)

    with col1:
        classification_model = st.selectbox(
            "Classification Model",
            options=list(MODEL_OPTIONS.keys()),
            index=1,  # Default to Llama Maverick (Balanced)
            help="Model used to classify document type",
        )

    with col2:
        extraction_model = st.selectbox(
            "Extraction Model",
            options=list(MODEL_OPTIONS.keys()),
            index=2,  # Default to Qwen (Accurate)
            help="Model used to extract document details",
        )

    # Display model info
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"ℹ️ {MODEL_OPTIONS[classification_model]['description']}")
    with col2:
        st.caption(f"ℹ️ {MODEL_OPTIONS[extraction_model]['description']}")

    st.markdown("---")

    # Run button
    if uploaded_file:
        if st.button("🚀 Run Extraction", type="primary"):
            process_document(
                uploaded_file,
                MODEL_OPTIONS[classification_model]["id"],
                MODEL_OPTIONS[extraction_model]["id"],
            )
    else:
        st.info("👆 Please upload a document to get started")


def process_document(uploaded_file, classification_model, extraction_model):
    """Process the uploaded document and display results."""

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(uploaded_file.name).suffix
    ) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Get API key from environment or session state
        api_key = os.environ.get("FIREWORKS_API_KEY", "fw_3ZdTBJnk2qnp1To57RM6KS8J")

        # Initialize extractor
        with st.spinner("Initializing extractor..."):
            extractor = KYCDocumentExtractor(
                api_key=api_key,
                classification_model=classification_model,
                extraction_model=extraction_model,
                run_validations=True,
            )

        # Stage 1: Classification
        st.markdown("### 📋 Processing Logs")

        with st.spinner("🔍 Stage 1: Classifying document type..."):
            base64_image = extractor.read_image(tmp_path)
            classification = extractor.classify_document(base64_image)

        doc_type = classification.get("document_type")
        confidence = classification.get("confidence", 0)

        # Check if valid ID
        if doc_type == "invalid":
            st.markdown(
                f"""
            <div class="error-box">
                <strong>❌ Invalid Document</strong><br>
                {classification.get('reasoning', 'Document could not be classified as a valid ID.')}
                <br><br>
                Please try again with a clear image of a passport, driver's license, or other ID.
            </div>
            """,
                unsafe_allow_html=True,
            )
            return

        # Valid ID - show success
        st.markdown(
            f"""
        <div class="success-box">
            <strong>✅ Valid ID Detected</strong><br>
            Document Type: <strong>{doc_type.replace('_', ' ').title()}</strong> (Confidence: {confidence:.0%})
            <br>
            Proceeding with extraction...
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Stage 2: Extraction
        with st.spinner(
            f"🔬 Stage 2: Extracting {doc_type.replace('_', ' ')} details..."
        ):
            result = extractor.extract_document_info(tmp_path)

        if result.get("status") != "success":
            st.error(f"❌ Extraction failed: {result.get('message', 'Unknown error')}")
            return

        # Show extraction complete
        st.markdown(
            """
        <div class="success-box">
            <strong>✅ Extraction Complete</strong><br>
            All fields have been successfully extracted and validated.
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Display Results
        display_results(result)

    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def display_results(result):
    """Display extraction results with confidence coloring."""

    st.markdown("## 📊 Extraction Results")

    # Essential Fields (Always visible)
    st.markdown("### 👤 Essential Information")

    essential = result.get("essential_fields", {})

    col1, col2 = st.columns(2)

    with col1:
        # Full Name
        name_data = essential.get("full_name", {})
        display_field("Full Name", name_data.get("value"), name_data.get("confidence"))

        # Date of Birth
        dob_data = essential.get("date_of_birth", {})
        display_field(
            "Date of Birth", dob_data.get("value"), dob_data.get("confidence")
        )

        # Age
        if result.get("age"):
            display_field("Age", f"{result['age']} years", 1.0)

    with col2:
        # Sex
        sex_data = essential.get("sex", {})
        display_field("Sex", sex_data.get("value"), sex_data.get("confidence"))

        # Address
        address_data = essential.get("address", {})
        if address_data.get("value"):
            display_field(
                "Address", address_data.get("value"), address_data.get("confidence")
            )

    # Document-Specific Metadata (Expandable)
    st.markdown("---")

    with st.expander("📋 Document Metadata", expanded=False):
        metadata = result.get("metadata", {})
        doc_type = result.get("document_type")

        if not metadata:
            st.info("No metadata available")
        else:
            # Display metadata in two columns
            items = list(metadata.items())
            mid = len(items) // 2 + len(items) % 2

            col1, col2 = st.columns(2)

            with col1:
                for key, value in items[:mid]:
                    if isinstance(value, dict):
                        label = key.replace("_", " ").title()
                        display_field(
                            label, value.get("value"), value.get("confidence")
                        )

            with col2:
                for key, value in items[mid:]:
                    if isinstance(value, dict):
                        label = key.replace("_", " ").title()
                        display_field(
                            label, value.get("value"), value.get("confidence")
                        )

    # Extraction Notes (Expandable)
    if result.get("extraction_notes"):
        with st.expander("📝 Extraction Notes", expanded=False):
            st.info(result["extraction_notes"])

    # Validation Results
    st.markdown("---")
    display_validation_results(result)

    # Cost Information
    if "_cost_info" in result:
        st.markdown("---")
        display_cost_info(result)


def display_cost_info(result):
    """Display cost information for the API calls."""

    cost_info = result.get("_cost_info", {})

    if not cost_info:
        return

    st.markdown("### 💰 Cost Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Cost",
            f"${cost_info['total_cost']:.6f}",
            help="Total cost for this extraction run",
        )

    with col2:
        st.metric(
            "Classification",
            f"${cost_info['classification_cost']:.6f}",
            help="Cost for document classification",
        )

    with col3:
        st.metric(
            "Extraction",
            f"${cost_info['extraction_cost']:.6f}",
            help="Cost for data extraction",
        )

    # Token usage details (expandable)
    with st.expander("📊 Token Usage Details", expanded=False):
        usage = cost_info.get("usage_stats", {})

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Classification:**")
            st.markdown(
                f"- Prompt Tokens: {usage.get('classification', {}).get('prompt_tokens', 0):,}"
            )
            st.markdown(
                f"- Completion Tokens: {usage.get('classification', {}).get('completion_tokens', 0):,}"
            )
            st.markdown(
                f"- Total: {usage.get('classification', {}).get('total_tokens', 0):,}"
            )

        with col2:
            st.markdown("**Extraction:**")
            st.markdown(
                f"- Prompt Tokens: {usage.get('extraction', {}).get('prompt_tokens', 0):,}"
            )
            st.markdown(
                f"- Completion Tokens: {usage.get('extraction', {}).get('completion_tokens', 0):,}"
            )
            st.markdown(
                f"- Total: {usage.get('extraction', {}).get('total_tokens', 0):,}"
            )

        st.markdown(f"**Grand Total: {usage.get('total_tokens', 0):,} tokens**")


def display_validation_results(result):
    """Display validation test results."""

    validation = result.get("_validation_results", {})

    if not validation.get("validation_run"):
        return

    st.markdown("### ✅ Validation Tests")

    total = validation["total_tests"]
    passed = validation["passed"]
    failed = validation["failed"]
    errors = validation["errors"]
    warnings = validation["warnings"]

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Tests", total)
    with col2:
        st.metric("Passed", passed, delta=f"{passed/total*100:.0f}%")
    with col3:
        st.metric(
            "Errors",
            errors,
            delta=f"-{errors}" if errors > 0 else "0",
            delta_color="inverse",
        )
    with col4:
        st.metric(
            "Warnings",
            warnings,
            delta=f"-{warnings}" if warnings > 0 else "0",
            delta_color="inverse",
        )

    # Show errors if present
    if errors > 0:
        with st.expander("❌ Error Details", expanded=True):
            for error in validation["error_details"]:
                st.markdown(
                    f"""
                <div class="error-box">
                    <strong>Test:</strong> {error['test']}<br>
                    <strong>Issue:</strong> {error['message']}
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # Show warnings if present
    if warnings > 0:
        with st.expander("⚠️ Warning Details", expanded=False):
            for warning in validation["warning_details"]:
                st.markdown(
                    f"""
                <div class="warning-box">
                    <strong>Test:</strong> {warning['test']}<br>
                    <strong>Note:</strong> {warning['message']}
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # All test results (Expandable)
    with st.expander("📋 All Test Results", expanded=False):
        test_results = validation.get("test_results", [])

        for test in test_results:
            status = (
                "✅"
                if test["passed"]
                else ("❌" if test["severity"] == "error" else "⚠️")
            )
            st.markdown(f"{status} **{test['test']}**: {test['message']}")


if __name__ == "__main__":
    main()
