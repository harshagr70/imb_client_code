# Financial Statement Extractor - Streamlit App

A user-friendly web interface for extracting financial statements (Income Statement, Balance Sheet, and Cash Flow Statement) from PDF documents.

## Features

- 📤 **PDF Upload**: Easy drag-and-drop PDF upload interface
- 🔍 **Automatic Extraction**: Automatically identifies and extracts financial statements
- 📊 **Table Display**: Beautiful, formatted tables for each financial statement
- 📥 **Excel Export**: Download all extracted data as a formatted Excel file
- 🎨 **Modern UI**: Clean, professional interface with intuitive navigation
- 🛰️ **Live Progress Log**: Real-time status updates so you can follow every pipeline step

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the necessary API keys:
   - **Parser API Key**: For PDF parsing
   - **Validator API Key**: For table validation and extraction

## Running the App

Start the Streamlit app with:

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Usage

1. **Enter API Keys**: In the sidebar, enter your parser and validator API keys
2. **Upload PDF**: Click "Browse files" or drag and drop a PDF file containing financial statements
3. **Extract**: Click the "Extract Financial Statements" button
4. **View Results**: The extracted statements will be displayed in separate sections
5. **Download**: Click "Download as Excel" to save all statements in Excel format

## Notes

- The app processes PDFs using the same pipeline as the notebook, but with a clean UI
- All pipeline logic is encapsulated and not exposed in the interface
- The Excel file includes proper formatting with headers, sections, and number formatting
- Processing time depends on PDF size and complexity

