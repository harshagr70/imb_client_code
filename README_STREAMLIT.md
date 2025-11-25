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

2. Set up API keys (choose one method):

### Option A: Using Streamlit Secrets (Recommended for Deployment)

**For Local Development:**
1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Replace the placeholder values with your actual API keys:
```toml
LLAMA_API_KEY = "your-actual-llama-parse-api-key"
OPENAI_API_KEY = "your-actual-openai-api-key"
```

**For Streamlit Cloud Deployment:**
1. Go to your app on [Streamlit Cloud](https://share.streamlit.io/)
2. Click on **"Settings"** → **"Secrets"**
3. Paste the following format (with your actual keys):
```toml
LLAMA_API_KEY = "your-actual-llama-parse-api-key"
OPENAI_API_KEY = "your-actual-openai-api-key"
```
4. Save - your app will automatically use these keys (no need to enter them in the UI!)

### Option B: Manual Entry (Fallback)

If secrets are not configured, you can enter API keys in the sidebar. They will be saved for your current session, so you only need to enter them once per browser session.

## Running the App

Start the Streamlit app with:

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Usage

1. **API Keys**: 
   - If using secrets: Keys are automatically loaded (no action needed)
   - If not using secrets: Enter your parser and validator API keys in the sidebar (once per session)
2. **Upload PDF**: Click "Browse files" or drag and drop a PDF file containing financial statements
3. **Extract**: Click the "Extract Financial Statements" button
4. **View Results**: The extracted statements will be displayed in separate sections
5. **Download**: Click "Download as Excel" to save all statements in Excel format

## Notes

- The app processes PDFs using the same pipeline as the notebook, but with a clean UI
- All pipeline logic is encapsulated and not exposed in the interface
- The Excel file includes proper formatting with headers, sections, and number formatting
- Processing time depends on PDF size and complexity

