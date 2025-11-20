import os
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from helpers.prompts import attention_prompt
from pydantic import BaseModel, Field
from pydantic import validator
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from langchain_core.documents import Document
import fitz
from typing import Literal
from helpers.prompts import attention_prompt2
from tqdm import tqdm

class attentionOutput(BaseModel):
    """
    A model representing the result of processing a document page to identify relevant financial information.

    Attributes:
        focus (bool): A boolean value indicating whether the page contains relevant financial information.
        page_description (str): Detailed description of the page content including tables and key financial terms.
        reason (str): Justification or explanation for the action performed.
    """

    focus: bool = Field(
        default=False,  # Default to False if not provided
        description="A boolean value indicating whether we should focus on the current page or not."
    )
    page_description: str = Field(
        default="",  # Default to empty string if not provided
        description="Detailed description on the page and what is included as tables with titles along with key financial terms (Balance Sheet, Income Statement, specific line items)."
    )
    reason: str = Field(
        default="",
        description="Justification or explanation for the action performed."
    )
    page_type: Literal["balance sheet", "income statement", "cashflow", "none"] = Field(
        default="none",
        description="Statement type detected on the page."
    )
    
    # Custom validator to set focus to True if page_description is non-empty and focus is missing
    @validator('focus', pre=True)
    def set_focus_from_description(cls, v, values):
        # If focus wasn't explicitly provided but we have a page description
        if v is None and 'page_description' in values and values['page_description']:
            # Automatically set focus to True if we have page content
            return True
        return v






_attention_model = None

def configure_attention_llm(api_key: str | None = None):
    """Configure the attention LLM with provided API key."""
    global _attention_model
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY must be provided either via argument or environment.")
    _attention_model = ChatOpenAI(model="gpt-4o", temperature=0, api_key=key)

def _get_attention_model():
    if _attention_model is None:
        configure_attention_llm()
    return _attention_model

def single_page_attention(page, is_not):
    structured_llm = _get_attention_model().with_structured_output(attentionOutput)

    if is_not :
        mdm_prompt = PromptTemplate(template = attention_prompt2, input_variables=["content"],   # for pulling comprehensive income if income statement not pressent
        )
    else :
        mdm_prompt = PromptTemplate(template = attention_prompt, input_variables=["content"],
        )
    
    ## default values for the coverse_cost : (changes made)
    converse_costs = {
        'total tokens': 0,
        'total cost': 0.0,
        'completion_tokens': 0,
        'prompt_tokens': 0
    }

    chain = mdm_prompt | structured_llm
    for attempt in range(3):
            
            try:
                with get_openai_callback() as cb:
                    result = chain.invoke({'content': page})
                converse_costs = {
                    'total tokens': cb.total_tokens,
                    'total cost': cb.total_cost,
                    'completion_tokens': cb.completion_tokens,
                    'prompt_tokens': cb.prompt_tokens
                 }
                break

            except Exception as e:
                print(str(e))
                if attempt == 3 - 1:  # Last attempt
                    result = {}

    return {'included': result.focus, 'reason':result.reason, 'type': result.page_type}, converse_costs

def process_pages_for_attention(pages, is_not,                                      # To trigger prompt for comprehensive income statement
                              single_page_processor=single_page_attention,
                              max_workers: int = 3,
                              batch_size: int = 10) -> Dict[int, Dict]:
    """
    Process multiple document pages to identify those containing relevant financial information.
    
    Args:
        pages: List of Document objects containing page content and metadata
        single_page_processor: Function that processes a single page (default: single_page_attention)
        max_workers: Maximum number of concurrent workers for processing
        batch_size: Number of pages to process in each batch
    
    Returns:
        Dict mapping page numbers to their attention results
    """
    def process_page_with_metadata(page) -> Dict:
        """Process a single page and include its metadata in the result"""
        result, cost = single_page_processor(page.page_content, is_not)
        return {
            'page_number': page.metadata.get('page', None),
            'included': result['included'],
            'reason': result['reason'],
            'type': result['type'],
            'cost': cost
        }
    
    def process_batch(batch) -> List[Dict]:
        """Process a batch of pages concurrently"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_page_with_metadata, batch))
        return results
    # Process pages in batches
    all_results = {}
    total_batches = (len(pages) + batch_size - 1) // batch_size
    
    for i in tqdm(range(0, len(pages), batch_size), total=total_batches, desc="Processing pages"):
        batch = pages[i:i + batch_size]
        batch_results = process_batch(batch)
        
        # Store results
        for result in batch_results:
            page_num = result['page_number']
            if page_num is not None:
                all_results[page_num] = {
                    'included': result['included'],
                    'reason': result['reason'],
                    'type': result['type'],
                    'cost': result['cost']
                    
                }

    return all_results



    ## pasting the transform document function here def transform_selected_documents(documents, selected_indices):  # Total original pages
def transform_selected_documents(documents, selected_indices):

    total_pages = len(documents)  # Total original pages

    transformed_list = []
    for new_index, original_index in enumerate(selected_indices):
        doc = documents[original_index]
        print("✅✅✅✅✅   PROCESS SELECTED DOC   ✅✅✅", original_index)
        
        metadata = doc.metadata if hasattr(doc, "metadata") else {}
        label = str(original_index + 1)  # original page label (1-based)

        transformed_metadata = {
            "producer": "Canva",
            "creator": "Canva",
            "creationdate": "2025-01-25T14:06:02+00:00",
            "title": metadata.get("file_name", ""),
            "moddate": "2025-01-25T14:06:00+00:00",
            "keywords": "DAGdNhvlV7k,BAGTkHG1Xfo",
            "author": "ilyes ben khalifa",
            "source": metadata.get("file_path", ""),
            "total_pages": total_pages,
            "page": original_index,
            "page_label": metadata.get("page_label", label)
        }
        page_content = getattr(doc, "Text", "")
        txt_resource = doc.text_resource.text + f"[The page number is {label} of {total_pages}]\n\n"
        transformed_list.append(Document(metadata=transformed_metadata, page_content=doc.text_resource.text))

    return transformed_list




def save_filtered_pages_as_pdf(original_pdf, included_pages, output_pdf="filtered_pages.pdf"):
    """Save selected pages into a new PDF while preserving layout."""
    doc = fitz.open(original_pdf)  # Load the original PDF
    new_pdf = fitz.open()  # Create a new empty PDF

    for page_num in included_pages:
        new_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)  # Copy the original pages

    new_pdf.save(output_pdf)  # Save the new PDF
    new_pdf.close()
    print(f"Filtered PDF saved as: {output_pdf}")
    return True


def get_included_pages(processed_results: Dict[int, Dict]) -> Dict[int, str]:
    included = {}
    for page_num, result in processed_results.items():
        if result.get('included') is True:
            page_type = result.get('type')
            if result.get('included') is True:
                page_type = result.get('type')
                included[page_num] = page_type if page_type else ''
    return included


    