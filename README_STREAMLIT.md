# KYC Document Extractor - Streamlit UI

A clean, professional web interface for AI-powered identity document processing.

## Features

### 🎨 Clean UI Design
- Modern gradient header
- Intuitive file upload
- Real-time processing feedback
- Confidence-based color coding (Red → Yellow → Green)

### 🔧 Model Selection
- **⚡ Fast (Qwen 32B)**: Quick processing, good accuracy
- **🎯 Balanced (Qwen 32B)**: Best balance (Default)
- **🔬 Accurate (Llama 90B)**: Slower but highest accuracy

### 📊 Results Display
- **Essential Fields**: Always visible with confidence colors
- **Document Metadata**: Expandable section with all document-specific details
- **Validation Tests**: Shows passed/failed tests with error details
- **Location Normalization**: Shows before/after normalization

### 🎯 Confidence Color Gradient
- **Green (1.0)**: 100% confidence - perfectly clear
- **Yellow-Green (0.7-0.9)**: High confidence
- **Yellow (0.5-0.6)**: Medium confidence
- **Orange-Red (0.0-0.4)**: Low confidence

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Fireworks API key (optional - defaults to hardcoded key):
```bash
export FIREWORKS_API_KEY="your-api-key"
```

## Running the App

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Upload Document**: Click "Upload Identity Document" and select an image
2. **Select Models**: Choose classification and extraction models (or use defaults)
3. **Click Run**: Press "🚀 Run Extraction" button
4. **View Results**:
   - If invalid, you'll see an error message
   - If valid, you'll see extraction progress and results

## UI Components

### Processing Flow
1. **Classification Log**: Shows if document is valid/invalid
2. **Extraction Log**: Shows extraction progress
3. **Essential Fields**: Name, DOB, Sex, Address with confidence colors
4. **Metadata (Expandable)**: Document-specific fields
5. **Validation Results**: Test summary with error/warning details
6. **Normalization (Expandable)**: Original vs normalized locations

### Confidence Display
Each field has:
- **Background color**: Shows confidence as gradient (red → green)
- **Confidence badge**: Percentage shown on the right
- **Border color**: Matches confidence level

### Validation Section
- **Metrics**: Total tests, passed, errors, warnings
- **Error Details**: Expandable with full explanations
- **Warning Details**: Expandable with minor issues
- **All Tests**: Complete list of all validation checks

## Example Screenshot Flow

1. **Landing Page**: Clean header, upload button, model dropdowns
2. **After Upload**: Image preview appears on the right
3. **Processing**: Spinner with "Classifying..." message
4. **Invalid ID**: Red error box with reason
5. **Valid ID**: Green success box with document type
6. **Extraction**: Progress spinner
7. **Results**: Essential fields with confidence colors
8. **Validation**: Test results with expandable errors/warnings

## Supported Documents
- ✅ Passports
- ✅ Driver's Licenses
- ✅ Other IDs (State ID, College ID, etc.)
- ❌ Invalid documents (shows error)

## Technical Details
- No changes to existing code logic
- Uses existing `KYCDocumentExtractor` class
- Temporary file handling for uploads
- Automatic cleanup of temp files
- Real-time processing feedback
- Responsive two-column layout

## Customization
You can modify the UI by editing `streamlit_app.py`:
- Colors: Update the CSS in the `st.markdown()` section
- Layout: Adjust column ratios
- Model options: Modify `MODEL_OPTIONS` dictionary
- Confidence colors: Change `get_confidence_color()` function
