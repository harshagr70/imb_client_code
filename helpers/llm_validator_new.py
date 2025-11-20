# robust_llm_validator.py

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
from jsonschema import validate, ValidationError
import asyncio
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ValidationOutput:
    data: Optional[Any] = None
    error: Optional[str] = None


# ----- SCHEMA -----
JSON_SCHEMA = {
    "type": "object",
    "required": ["statement_type", "periods", "units", "rows"],
    "properties": {
        "statement_type": {"type": "string", "enum": ["income_statement", "balance_sheet", "cash_flow"]},
        "units": {
            "type": "object",
            "required": ["currency", "scale"],
            "properties": {
                "currency": {"type": "string"},
                "scale": {"type": "string"}
            }
        },
        "periods": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "required": ["label", "date", "year"],
                "properties": {
                    "label": {"type": "string"},
                    "date": {"type": "string"},
                    "year": {"type": "integer"}
                }
            }
        },
        "rows": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["label", "values"],
                "properties": {
                    "label": {"type": "string"},
                    "values": {"type": "object"},
                    "is_section": {"type": "boolean"},
                    "section_id": {"type": "string"}  # NEW FIELD: tracks which section this row belongs to
                }
            }
        },
        "notes": {"type": "array", "items": {"type": "string"}}
    }
}

# ----- LLM CLIENT -----
class LLMClient:
    def chat(self, model: str, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

class OpenAILLM(LLMClient):
    def __init__(self, api_key:str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    def chat(self, model:str, system_prompt:str, user_prompt:str) -> str:
        resp = self.client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role":"system","content":system_prompt},
                {"role":"user","content":user_prompt}
            ]
        )
        return resp.choices[0].message.content

# ----- PROMPT -----
SYSTEM_PROMPT = """
You are a robust financial table parser.  
Convert messy financial tables into STRICT JSON that matches the schema below.
---
### Schema
- `statement_type`: `"income_statement"` | `"balance_sheet"` | `"cash_flow"`
- `units`: `{currency, scale}`
- `periods`: list of `{year, date (ISO), label}`
- `rows`: list of `{label, section_id, is_section, values}`
---
### Parsing Rules
1. **Detect statement_type**  
   - One of: `income_statement`, `balance_sheet`, `cash_flow`.

2. **Units**  
   - Detect millions/thousands/billions from headers or context.  
   - Default currency = USD.

3. **Periods**  
   - Keep the original descriptive label exactly as written.  
   - Normalize dates:  
     * Year-only → `date = YYYY-12-31`  
     * Full date → `YYYY-MM-DD` (ISO format)  
     * Quarters → approximate quarter end date  
   - Row `values` MUST use only the bare year as keys (e.g., `{"2024": 12345}`), never full period labels.

4. **Numbers**  
   - Strip commas, currency signs, percent symbols.  
   - Parentheses = negative values.  
   - Empty/blank cells → `null`.  
   - Preserve all numbers exactly as they appear after normalization.

5. **CRITICAL: Strict Sequential Section Assignment**
   
   **Initialize:** `current_section = "document_opening"`
   
   **For each row, process in exact top-to-bottom order:**
   
   **A. Section Header Detection (is_section = True):**
   - Lines ending with ":" (colon)
   - Lines in ALL CAPS with no numerical values  
   - Pure text labels with no data values across all periods
   - Lines that are clearly structural headers/dividers
   
   **B. When Section Header Detected:**
   - Set `is_section = True`
   - Update `current_section = normalize_header_text(header)`
   - Normalization: lowercase, replace spaces with underscores, remove special characters, truncate to 50 chars
   - Examples:
     * "Operating activities:" → `current_section = "operating_activities"`
     * "Adjustments to reconcile net income:" → `current_section = "adjustments_to_reconcile_net_income"`
     * "Changes in operating assets and liabilities:" → `current_section = "changes_in_operating_assets_and_liabilities"`
   - Assign `section_id = current_section` to the header row
   
   **C. When Data Row Detected:**
   - Set `is_section = False`  
   - Assign `section_id = current_section` (inherit from most recent header)
   - NEVER leave `section_id` empty or null
   
   **D. Absolute Rules:**
   - EVERY header immediately updates `current_section` - no exceptions
   - NO nesting logic - treat every header as flat section boundary
   - NO parent-child relationships - each section is independent
   - If multiple consecutive headers appear, line items belong to the LAST header before them
   - Items at document start (before first header) get `section_id = "document_opening"`
   
   **E. Validation:**
   - Every row must have a non-empty `section_id`
   - Section IDs must be consistent within same statement type
   - Headers and their child items must have same `section_id`

6. **Enhanced Duplicate Detection**
   - Maintain set of `normalized_labels` for current statement
   - Normalize: `label.lower().strip().replace(/[^\w\s]/g, '').replace(/\s+/g, ' ')`
   - Before adding row: check if normalized label exists
   - Skip duplicates EXCEPT:
     * Section headers (`is_section = True`) - always allow
     * Labels starting with "Total", "Net", "Gross", "Basic", "Diluted" - allow multiples
     * Same label in different sections - allow if section_ids differ
   - If 3+ consecutive identical normalized labels: stop parsing (end of legitimate data)

7. **Quality Controls**
   - Preserve ALL rows exactly as they appear in source
   - DO NOT invent, modify, or skip any data
   - DO NOT merge or combine rows
   - Maintain exact order from source table
   - Every row gets processed - no exceptions

8. **Output Requirements**
   - Valid JSON only - no commentary, explanations, or extra text
   - All fields required as per schema
   - Consistent section_id naming within each statement
   - Complete data preservation

CRITICAL: Output must be a raw JSON object, not a string.
- Do NOT wrap the JSON in quotes.
- Do NOT escape quotes inside the JSON.
- Do NOT return Markdown code fences (```).
Return ONLY the bare JSON object.

---
### Examples of Correct Section Assignment

**Cash Flow Example:**
Row 1: "OPERATING ACTIVITIES:" → current_section="operating_activities", is_section=True
Row 2: "Net income" → section_id="operating_activities", is_section=False
Row 3: "Adjustments to reconcile:" → current_section="adjustments_to_reconcile", is_section=True
Row 4: "Depreciation" → section_id="adjustments_to_reconcile", is_section=False
Row 5: "Changes in assets:" → current_section="changes_in_assets", is_section=True
Row 6: "Accounts receivable" → section_id="changes_in_assets", is_section=False

**Critical:** Each header creates its own section. Sub-headers do NOT inherit parent sections.

---
### Goal
Perfect reconstruction capability where `GROUP BY section_id ORDER BY original_position` recreates the exact source table structure and sequence. The merger depends on this precision.

"""
USER_TEMPLATE = """JSON_SCHEMA:
{schema}

TASK:
Parse this table into strict JSON:

CONTENT:
{snippet}
"""

@dataclass
class ValidationResult:
    data: Dict[str,Any]

# ----- VALIDATOR -----
class LLMOnlyFinancialTableValidator:
    def __init__(self,llm:LLMClient,model="gpt-4.1"):
        self.llm = llm
        self.model = model

    def run(self,page_text:str)->ValidationResult:
        user_prompt = USER_TEMPLATE.format(schema=json.dumps(JSON_SCHEMA,ensure_ascii=False),snippet=page_text.strip())
        raw = self.llm.chat(self.model,SYSTEM_PROMPT,user_prompt)
        data = self._validate_or_retry(raw,SYSTEM_PROMPT,user_prompt)
        normalized = self._normalize(data)
        return ValidationResult(data=normalized)

    def _validate_or_retry(self,raw,system,user,retries=2):
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        last_err=None
        for i in range(retries+1):
            try:
                obj=json.loads(cleaned)
                validate(instance=obj,schema=JSON_SCHEMA)
                return obj
            except (json.JSONDecodeError,ValidationError) as e:
                last_err=str(e)
                if i<retries:
                    fix=user+"\nPREVIOUS ERROR:"+last_err+"\nRe-output ONLY strict JSON."
                    cleaned=self.llm.chat(self.model,system,fix).strip()
        raise ValueError("Validator failed:"+str(last_err))

    def _normalize(self,obj:Dict[str,Any])->Dict[str,Any]:
        # Normalize periods
        for p in obj.get("periods",[]):
            if isinstance(p.get("year"),str) and p["year"].isdigit():
                p["year"]=int(p["year"])
            if not p.get("date") and isinstance(p.get("year"),int):
                p["date"]=f"{p['year']}-12-31"

        # Normalize rows
        period_keys=[str(p["year"]) for p in obj.get("periods",[])]
        for r in obj.get("rows",[]):
            # Guarantee values is always a dict
            vals=r.get("values") or {}
            if not isinstance(vals,dict):
                vals={}

            cleaned={}
            for k in period_keys:
                v=None
                # try exact match
                if k in vals:
                    v=vals.get(k)
                else:
                    # rescue verbose keys e.g. "52 Weeks Ended September 1, 2024"
                    for vk,vv in vals.items():
                        if k in str(vk):
                            v=vv
                            break
                cleaned[k]=self._coerce(v)

            r["values"]=cleaned

            # Detect sections
            if "is_section" not in r:
                if all(v is None for v in cleaned.values()) and r["label"].isupper():
                    r["is_section"]=True

        return obj

    def _coerce(self,v:Any)->Optional[float]:
        if v is None: return None
        if isinstance(v,(int,float)): return float(v)
        if isinstance(v,str):
            s=v.strip().replace(",","")
            if not s or s.lower() in {"na","n/a","–","—","-"}: return None
            neg=s.startswith("(") and s.endswith(")")
            s=s.strip("()$€£¥ ")
            try: num=float(s); return -num if neg else num
            except: return None
        return None

# ----- RUNNER -----
async def run_validator_on_pages_llm(vt, selected_pages: List[Dict[str, Any]], max_concurrency: int = 3):
    sem = asyncio.Semaphore(max_concurrency)

    async def _process(i, page):
        async with sem:
            try:
                res = await asyncio.to_thread(vt.run, page["page_content"])
                # If vt.run already returns a ValidationResult with .data, wrap it cleanly
                if hasattr(res, "data"):
                    return i, ValidationOutput(data=res.data)
                else:
                    return i, ValidationOutput(data=res)  # assume it's already a dict/json
            except Exception as e:
                return i, ValidationOutput(error=str(e))

    tasks = [asyncio.create_task(_process(i, p)) for i, p in enumerate(selected_pages)]
    out = await asyncio.gather(*tasks)
    out.sort(key=lambda x: x[0])
    return [r for _, r in out]

