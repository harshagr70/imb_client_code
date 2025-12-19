import streamlit as st
import pandas as pd
import asyncio
import tempfile
import os
from pathlib import Path
import json
import re
from io import BytesIO
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, List, Optional
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
import sys
import fitz

# Import pipeline from v3
from pipelines.financial_statement_extractor_v3 import (
    process_pdf_pipeline,
    json_to_dataframe,
    create_excel_file
)

# Page configuration
st.set_page_config(
    page_title="Financial Table Extractor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .statement-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    .page-preview-card {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .page-preview-card.selected {
        border-color: #3498db;
        background-color: #e8f4f8;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'latest_logs' not in st.session_state:
    st.session_state.latest_logs = []
if 'latest_progress' not in st.session_state:
    st.session_state.latest_progress = 0
if 'page_sources' not in st.session_state:
    st.session_state.page_sources = {}
if 'uploaded_pdf_bytes' not in st.session_state:
    st.session_state.uploaded_pdf_bytes = None
if 'page_previews' not in st.session_state:
    st.session_state.page_previews = {}
if 'parsed_pages' not in st.session_state:
    st.session_state.parsed_pages = False
if 'filtered_pages' not in st.session_state:
    st.session_state.filtered_pages = []
if 'selected_pages' not in st.session_state:
    st.session_state.selected_pages = set()
if 'validated_results' not in st.session_state:
    st.session_state.validated_results = []

def get_page_preview_image(page_number: Optional[int]) -> Optional[bytes]:
    """Render and cache a PDF page preview."""
    if page_number is None or st.session_state.uploaded_pdf_bytes is None:
        return None

    cache_key = f"page_{page_number}"
    if cache_key in st.session_state.page_previews:
        return st.session_state.page_previews[cache_key]

    try:
        with fitz.open(stream=st.session_state.uploaded_pdf_bytes, filetype="pdf") as doc:
            if page_number < 0 or page_number >= doc.page_count:
                return None
            page = doc.load_page(page_number)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image_bytes = pix.tobytes("png")
            st.session_state.page_previews[cache_key] = image_bytes
            return image_bytes
    except Exception:
        return None

def render_audit_view(result: Dict):
    """Render auditing view for a validated result with enhanced metadata."""
    page_number = result.get("page_number", 0)
    page_index = result.get("page_index", 0)
    data = result.get("data")
    error = result.get("error")
    table_metadata = result.get("table_metadata")
    explanation = result.get("explanation")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**📄 Source Page Preview**")
        image_bytes = get_page_preview_image(page_index)
        if image_bytes:
            st.image(image_bytes, use_container_width=True, caption=f"Original Page {page_number + 1}")
        else:
            st.info(f"Preview unavailable for page {page_number + 1}")
        
        # Show page metadata
        metadata = result.get("metadata", {})
        with st.expander("📋 Page Metadata"):
            st.json(metadata)
        
        # Show validation info
        if data:
            st.info("✅ Validation successful")
    
    with col2:
        if error and not explanation:
            st.error(f"**Validation Error:** {error}")
        elif data:
            # Show table metadata if available
            if table_metadata:
                st.markdown("### 📊 Table Information")
                title = table_metadata.get("table_title", "Financial Table")
                st.markdown(f"**Title:** {title}")
                
                description = table_metadata.get("table_description", "")
                if description:
                    st.markdown(f"**Description:** {description}")
                
                data_quality = table_metadata.get("data_quality", "")
                if data_quality:
                    quality_color = {"complete": "🟢", "partial": "🟡", "fragmented": "🟠", "estimated": "🔵"}.get(data_quality.lower(), "⚪")
                    st.markdown(f"**Data Quality:** {quality_color} {data_quality.title()}")
                
                key_insights = table_metadata.get("key_insights", [])
                if key_insights:
                    with st.expander("💡 Key Insights"):
                        for insight in key_insights:
                            st.markdown(f"• {insight}")
                
                context_notes = table_metadata.get("context_notes", "")
                if context_notes:
                    with st.expander("📝 Context Notes"):
                        st.info(context_notes)
            
            # Show explanation if available
            if explanation:
                with st.expander("📖 Table Explanation"):
                    st.markdown(explanation)
            
            statement_type = data.get("statement_type", "unknown")
            st.markdown(f"**Statement Type:** `{statement_type.replace('_', ' ').title()}`")
            
            units = data.get("units", {})
            if units:
                currency = units.get("currency", "N/A")
                scale = units.get("scale", "N/A")
                st.markdown(f"**Currency:** `{currency}` | **Scale:** `{scale}`")
            
            periods = data.get("periods", [])
            if periods:
                period_labels = [p.get("label", "N/A") for p in periods]
                st.markdown(f"**Periods:** {', '.join(period_labels[:3])}{'...' if len(period_labels) > 3 else ''}")
            
            # Download individual JSON
            json_str = json.dumps(data, indent=2)
            st.download_button(
                label=f"📥 Download JSON (Page {page_number + 1})",
                data=json_str,
                file_name=f"page_{page_number + 1}_statement.json",
                mime="application/json",
                key=f"download_json_{page_index}"
            )
            
            # Show raw JSON in expander
            with st.expander("🔍 View Raw JSON Data"):
                st.code(json_str, language="json")
        else:
            st.warning("No data available for this page.")
    
    st.markdown("---")

def main():
    # Header
    st.markdown('<div class="main-header">📊 Financial Table Extractor</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Helper function to get API keys
    def get_api_key(key_name: str, display_name: str, help_text: str) -> str:
        """Get API key from secrets, session state, or user input."""
        try:
            if key_name in st.secrets:
                return st.secrets[key_name]
        except (AttributeError, KeyError):
            pass
        
        session_key = f"{key_name}_stored"
        if session_key in st.session_state and st.session_state[session_key]:
            return st.session_state[session_key]
        
        entered_key = st.text_input(
            display_name,
            type="password",
            help=help_text,
            key=f"{key_name}_input"
        )
        
        if entered_key:
            st.session_state[session_key] = entered_key
            return entered_key
        
        return ""
    
    # Sidebar for API keys and upload
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        try:
            has_secrets = "LLAMA_API_KEY" in st.secrets and "OPENAI_API_KEY" in st.secrets
            if has_secrets:
                st.success("✅ API keys configured (using secrets)")
            else:
                st.info("💡 Enter API keys below (saved for this session)")
        except (AttributeError, KeyError):
            st.info("💡 Enter API keys below (saved for this session)")
        
        llama_api_key = get_api_key(
            "LLAMA_API_KEY",
            "LlamaParse API Key",
            "Enter the API key for LlamaParse"
        )
        
        openai_api_key = get_api_key(
            "OPENAI_API_KEY",
            "OpenAI API Key",
            "Enter the API key for OpenAI"
        )
        
        st.markdown("---")
        
        st.header("📤 Upload PDF")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF containing financial statements"
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
    
    # Main content area
    if not llama_api_key or not openai_api_key:
        st.info("👈 Please enter API keys in the sidebar to begin")
        return
    
    if st.session_state.uploaded_file is None:
        st.info("👈 Please upload a PDF file in the sidebar to begin extraction.")
        return
    
    # Step 1: Parse and filter (automatic on upload)
    if st.session_state.parsed_pages == False:
        st.markdown("### Step 1: Parsing PDF and Identifying Pages with Tables")
        
        progress_placeholder = st.empty()
        progress_bar = progress_placeholder.progress(0)
        log_placeholder = st.empty()
        
        status_icon_map = {
            "info": "ℹ️",
            "running": "⏳",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        def ui_log(message, status="info"):
            icon = status_icon_map.get(status, "ℹ️")
            st.session_state.latest_logs.append(f"{icon} {message}")
            log_placeholder.markdown("  \n".join(st.session_state.latest_logs))
        
        def ui_progress(current_step, total_steps):
            total = max(total_steps, 1)
            percentage = int(min(max((current_step / total) * 100, 0), 100))
            st.session_state.latest_progress = percentage
            progress_bar.progress(percentage)
        
        # Save uploaded file temporarily
        uploaded_bytes = st.session_state.uploaded_file.getvalue()
        st.session_state.uploaded_pdf_bytes = uploaded_bytes
        st.session_state.page_previews = {}
        st.session_state.latest_logs = []
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_bytes)
            tmp_path = tmp_file.name
        
        try:
            ui_progress(0, 2)
            # Parse and filter using pipeline
            validated_results, filtered_pages, error = process_pdf_pipeline(
                tmp_path,
                llama_api_key,
                openai_api_key,
                log_callback=ui_log,
                progress_callback=ui_progress
            )
            
            if error:
                st.error(f"❌ Error: {error}")
            else:
                st.session_state.parsed_pages = True  # Mark as parsed
                st.session_state.filtered_pages = filtered_pages
                st.success(f"✅ Found {len(filtered_pages)} pages with tables!")
                ui_progress(2, 2)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    # Step 2: Display pages with checkboxes (only if not yet processed)
    if st.session_state.filtered_pages and not st.session_state.processing_complete:
        st.markdown("---")
        st.markdown("### Step 2: Select Pages to Export")
        st.info(f"Found {len(st.session_state.filtered_pages)} pages with tables. Select which pages you want to extract and validate.")
        
        # Initialize selected pages if not set
        if not st.session_state.selected_pages:
            st.session_state.selected_pages = set()
        
        # Select All / Deselect All buttons
        col_sel1, col_sel2, col_sel3 = st.columns([1, 1, 2])
        with col_sel1:
            if st.button("✅ Select All", use_container_width=True):
                st.session_state.selected_pages = {page["index"] for page in st.session_state.filtered_pages}
                st.rerun()
        with col_sel2:
            if st.button("❌ Deselect All", use_container_width=True):
                st.session_state.selected_pages = set()
                st.rerun()
        with col_sel3:
            st.markdown(f"**Selected:** {len(st.session_state.selected_pages)} / {len(st.session_state.filtered_pages)} pages")
        
        st.markdown("---")
        
        # Display pages with checkboxes
        for idx, page_data in enumerate(st.session_state.filtered_pages):
            page_num = page_data["page_number"]
            page_index = page_data["index"]
            
            # Create a card for each page
            is_selected = page_index in st.session_state.selected_pages
            
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                checkbox_key = f"select_page_{page_index}"
                selected = st.checkbox(
                    "",
                    value=is_selected,
                    key=checkbox_key
                )
                
                # Update selection state
                if selected != is_selected:
                    if selected:
                        st.session_state.selected_pages.add(page_index)
                    else:
                        st.session_state.selected_pages.discard(page_index)
            
            with col2:
                st.markdown(f"**Page {page_num + 1}**")
                
                # Show page preview
                image_bytes = get_page_preview_image(page_index)
                if image_bytes:
                    st.image(image_bytes, use_container_width=True, caption=f"Page {page_num + 1}")
                
                # Show page content preview (first 500 chars)
                page_content = page_data["page_content"]
                preview_text = page_content[:500] + "..." if len(page_content) > 500 else page_content
                with st.expander(f"View page content (Page {page_num + 1})"):
                    st.text(preview_text)
                
                # Show filter result info
                filter_result = page_data.get("filter_result", {})
                stype = filter_result.get("type", "unknown")
                if stype != "neither":
                    st.caption(f"Detected type: {stype.replace('_', ' ').title()}")
            
            st.markdown("---")
        
        # Export button
        st.markdown("---")
        if st.button("🚀 Export Selected Tables", type="primary", use_container_width=True):
            if not st.session_state.selected_pages:
                st.warning("⚠️ Please select at least one page to export.")
            else:
                # Get selected pages data
                selected_pages_data = [
                    page for page in st.session_state.filtered_pages
                    if page["index"] in st.session_state.selected_pages
                ]
                
                # Get selected indices
                selected_indices = list(st.session_state.selected_pages)
                
                # Validate selected pages using pipeline
                progress_bar_validate = st.progress(0)
                status_placeholder = st.empty()
                
                def validate_log(message, status="info"):
                    status_icon_map = {
                        "info": "ℹ️",
                        "running": "⏳",
                        "success": "✅",
                        "warning": "⚠️",
                        "error": "❌"
                    }
                    icon = status_icon_map.get(status, "ℹ️")
                    status_placeholder.markdown(f"{icon} {message}")
                
                try:
                    validate_log("Starting validation...", "running")
                    progress_bar_validate.progress(0.3)
                    
                    # Save uploaded file temporarily again for validation
                    uploaded_bytes = st.session_state.uploaded_file.getvalue()
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_bytes)
                        tmp_path = tmp_file.name
                    
                    # Use pipeline to validate selected pages
                    validated_results, filtered_pages, error = process_pdf_pipeline(
                        tmp_path,
                        llama_api_key,
                        openai_api_key,
                        selected_page_indices=selected_indices,
                        log_callback=validate_log,
                        progress_callback=lambda c, t: progress_bar_validate.progress(c / t)
                    )
                    
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    
                    progress_bar_validate.progress(1.0)
                    st.session_state.validated_results = validated_results
                    st.session_state.processing_complete = True
                    
                    success_count = len([r for r in validated_results if r.get('data')])
                    st.success(f"✅ Successfully validated {success_count} out of {len(validated_results)} pages!")
                    st.rerun()
                except Exception as e:
                    progress_bar_validate.progress(1.0)
                    st.error(f"❌ Validation error: {str(e)}")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
    
    # Step 3: Display validated results
    if st.session_state.processing_complete and st.session_state.validated_results:
        st.markdown("---")
        st.markdown("### Step 3: Extracted Tables")
        
        # Download all button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            excel_file = create_excel_file(st.session_state.validated_results)
            st.download_button(
                label="📥 Download All as Excel",
                data=excel_file,
                file_name="financial_tables.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # Display each validated result
        for idx, result in enumerate(st.session_state.validated_results):
            data = result.get("data")
            error = result.get("error")
            page_num = result.get("page_number", idx)
            
            if error:
                st.error(f"**Page {page_num + 1} - Validation Error:** {error}")
                st.markdown("---")
                continue
            
            if data:
                statement_type = data.get("statement_type", "unknown")
                st.markdown(f'<div class="statement-header">Page {page_num + 1}: {statement_type.replace("_", " ").title()}</div>', unsafe_allow_html=True)
                
                # Display table
                df = json_to_dataframe(data)
                if df is not None:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Unable to convert data to table format.")
                
                # Auditing section
                st.markdown("#### 🔍 Auditing & Verification")
                render_audit_view(result)
            else:
                st.warning(f"**Page {page_num + 1}:** No data extracted.")
                st.markdown("---")
        
        # Reset button
        st.markdown("---")
        if st.button("🔄 Process Another PDF", use_container_width=True):
            st.session_state.processing_complete = False
            st.session_state.extracted_data = {}
            st.session_state.uploaded_file = None
            st.session_state.page_sources = {}
            st.session_state.uploaded_pdf_bytes = None
            st.session_state.page_previews = {}
            st.session_state.parsed_pages = []
            st.session_state.filtered_pages = []
            st.session_state.selected_pages = set()
            st.session_state.validated_results = []
            st.rerun()

if __name__ == "__main__":
    main()
