import re
from typing import List, Dict, Any

def markdown_table_to_json(md_text: str) -> List[Dict[str, Any]]:
    lines = md_text.strip().splitlines()
    result = []
    current_section = {"section": None, "rows": []}
    headers = []
    in_table = False

    def clean_number(val: str):
        val = val.replace("$", "").replace(",", "").replace("**", "").replace("—", "").strip()
        if val.startswith("(") and val.endswith(")"):
            val = "-" + val[1:-1]
        try:
            return float(val)
        except:
            return None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect potential table header row
        if line.startswith("|") and "|" in line[1:]:
            # Check next line is a valid markdown separator line
            if i + 1 < len(lines) and re.match(r"\|\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$", lines[i + 1].strip()):
                headers = [h.strip() for h in line.strip("|").split("|")]
                i += 2  # Skip to first data row
                in_table = True
                continue

        # Stop if we've passed the table and hit non-table content
        if in_table and not line.startswith("|"):
            break

        # While inside a valid table
        if in_table:
            parts = [p.strip() for p in line.strip("|").split("|")]

            # Handle section headers like "**LIABILITIES**"
            if re.fullmatch(r"\*\*[A-Z \-’]+\*\*", parts[0]):
                if current_section["section"] or current_section["rows"]:
                    result.append(current_section)
                    current_section = {"section": None, "rows": []}
                current_section["section"] = parts[0].replace("**", "").strip()
                i += 1
                continue

            label = parts[0]
            value_parts = parts[1:]

            # Skip empty lines
            if not label and all(v == "" for v in value_parts):
                i += 1
                continue

            values = {}
            for j in range(1, len(headers)):
                key = headers[j]
                val = value_parts[j - 1] if j - 1 < len(value_parts) else ""
                values[key] = clean_number(val)

            current_section["rows"].append({
                "label": label.replace("**", "").strip(),
                "values": values
            })

        i += 1

    if current_section["section"] or current_section["rows"]:
        result.append(current_section)

    return result




def get_ordered_dicts_from_pages(transformed_documents, included_pages):
    """
    Returns a list of page dicts in the order specified by included_pages.

    Args:
        transformed_documents: List of document objects with metadata['page']
        included_pages: List or Dict of page numbers to include (e.g., [89, 70, 94] or {89: 'type'})

    Returns:
        List of dicts (as_dicts) in the order of included_pages
    """
    # Support both list and dict input for included_pages
    page_nums = list(included_pages)  # works whether it's a list or a dict (takes keys)

    # Map page_num → page object
    page_map = {page.metadata['page']: page for page in transformed_documents}

    # Extract in correct order and convert to dicts
    return [page_map[page_num].__dict__ for page_num in page_nums if page_num in page_map]