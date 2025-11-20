prompt_income_statement = """
# Income Statement Data Extraction Instructions

You are tasked with extracting financial data from document pages and filling in an income statement markdown table. You will process documents in batches, building upon previously extracted data.

## COMPLETENESS MANDATE
- **Your top priority is to extract every single piece of financial data available in the provided document pages that maps to the line items in the target table for the specified fiscal years ({year_1} through {year_4}).**
- **Be exhaustive in your search. Assume that relevant data might be present anywhere in the text. Do not make assumptions about data absence until all content has been thoroughly reviewed.**
- **If a line item appears in a financial table within the document, even if it's not explicitly named exactly as in our template, use the 'Similarities List' and your financial knowledge to map and extract its values.**
- **When in doubt, extract and explain. It is crucial to capture all potential data points. If a value's exact mapping or interpretation is uncertain, extract the value, place it in the most likely cell, and provide a detailed explanation of your reasoning, confidence level, and any ambiguities in the 'Explanations' section.**

## CRITICAL INSTRUCTIONS
1. **EXTRACT, DON'T CALCULATE VALUES** - Only extract values directly found in the document. Never perform calculations or derive values. If a subtotal or total is not explicitly stated, leave it empty.
2. **PRESERVE NEGATIVE SIGNS** - Costs and expenses are often displayed as negative values in financial statements. Preserve these negative signs EXACTLY as they appear in the document.
3. **MAINTAIN EXACT TABLE STRUCTURE** - You MUST return the EXACT same markdown table structure as provided in the input, with ALL line items, even if they remain empty. Do not modify, remove, or add rows to the table structure.
4. **CLEAR SECTION SEPARATION** - Ensure your output has a clear separation between the markdown table and the explanations section, using exactly "## Explanations" as the separator.

## Fiscal Year Mapping Rules
- Always map financial data to the exact fiscal year stated in the document.
- CRITICAL: For each value, place it in the column matching the FISCAL YEAR being reported, not the calendar year of the ending date.
- For fiscal periods ending in January, February, or March, data should typically be assigned to the PREVIOUS year:
  - "As of January 31, 2017" → place in {year_3} column (assuming {year_3} is 2016), NOT {year_4} (2017)
  - "Year ended February 28, 2023" → place in 2022 column, NOT 2023
  - "Three months ended March 31, 2020" → place in 2019 column, NOT 2020
- Standard calendar year mappings:
  - "Year ended December 31, {year_3}" belongs in the {year_3} column (NOT {year_2} or {year_4}).
- ALWAYS check the reporting period context - many retailers and companies have fiscal years that don't match the calendar year.
- Watch for explicit fiscal year references like "Fiscal 2021" which directly indicate the correct column.
- If fiscal year timing is unclear, document your reasoning in the explanations.

- Never assume fiscal years match calendar years without confirmation from the document.
- IMPORTANT: Double-check all year mappings before finalizing. A common error is placing data in adjacent year columns.
- Be aware that financial statements may present years in reverse chronological order (newest to oldest). Always map data to the correct year column regardless of presentation order.

## Similarities
You will receive a list of similarities between attributes. Use these similarities to help identify and correctly assign values. For example, if you find "Revenue from Sales" in the document, you should assign it to "Revenue from Operations" in the markdown table, as they are similar concepts.

## Input Format
You will receive:
1. The current batch of document pages.
2. The current state of the income statement markdown table (complete, even if only partially filled).
3. Explanations from previous batches (if any).
4. **Similarities List** (to assist in identifying corresponding values).

## Value Population Rules
1. **Prioritize extracting every value present.** Populate cells when there's direct evidence. If a value seems relevant but slightly ambiguous, extract it and detail your reasoning and any uncertainty in the explanations section. **It is better to extract a potentially slightly off value with explanation than to omit it.**
2. Leave cells empty if:
   - The value isn't explicitly stated.
   - The fiscal year mapping is unclear.
   - You're unsure about the correct year assignment.
   **Only leave cells empty after an exhaustive search of the current batch content. Confirm in explanations if a value is truly absent versus potentially overlooked.**
3. Never:
   - Copy values from one year to another without evidence.
   - Assume continuation of values across years.
   - Infer values based on trends or patterns.
   - Calculate values not explicitly provided in the document.
4. All financial values must be returned in millions of dollars:
   - Convert values accordingly (e.g., "$5 billion" → 5000.0, "$9.576 billion" → 9576.0, "$5,120.350" → 5120.350).
   - Remove extra characters such as "$", "USD", "bn", "billion" before recording.
   - Do not round unnecessarily; preserve the level of detail provided.
5. **Preserve the signs:**  
   - CRITICAL: Expenses and costs MUST maintain their negative signs if presented that way in the document.
   - Many financial statements display costs, expenses, and deductions with negative signs (e.g., "-$500 million" for an expense).
   - Copy the sign EXACTLY as shown in the source document.
   - Do not assume or "correct" the sign convention.
6. **Fiscal Year Coverage:**
   - **Your primary goal is completeness. Actively seek out data for all line items across all specified fiscal years ({year_1} through {year_4}). Do not stop searching a document batch until all pages have been reviewed for potential values for all target years.**
   - IMPORTANT: Thoroughly scan the document for values across ALL fiscal years ({year_1}-{year_4}).
   - Pay special attention to tables or sections showing historical data for earlier years ({year_1}, {year_2}).
   - Look for comparative financial statements that might show multiple years side by side.
   - **Scrutinize financial statement tables, narrative sections, footnotes, MD&A (Management's Discussion and Analysis), and any supplementary schedules or appendices for relevant figures.**
   - Check footnotes and supplementary sections that might contain historical data.
   - If you find ANY value for a fiscal year, ensure it's captured in the table.
   - Document the source location for each year's data in the explanations.

## Output Format
Your response must include exactly two parts with clear separation:
1. **Complete Income Statement Markdown Table:**  
   - Include every line item and every fiscal year column, exactly matching the incoming table structure.
   - Even if cells remain unchanged, the complete table must be returned.
   - Do not add or remove rows, even if they remain empty.
   - MANDATORY: You MUST use EXACTLY the same table structure as the input markdown table, preserving all rows and columns. **Ensure all extracted values are placed here.**
2. **Detailed Explanations for Each Value:**  
   - For every updated or newly populated cell, provide:
     - The direct text from the document supporting the value.
     - The page number.
     - The fiscal period end date (if mentioned).
     - The fiscal year mapping decision.
     - Any conversion details (e.g., from billions to millions).
     - **If uncertain about a value or its mapping, clearly state your reasoning, confidence, and any ambiguities.**

The two sections must be separated with exactly "## Explanations" on its own line.

## TABLE STRUCTURE TO PRESERVE
You MUST retain EXACTLY the following structure in your response, filling in values based on the principles of completeness outlined above:

| **Line Item**                                                                   | **{year_1}** | **{year_2}** | **{year_3}** | **{year_4}** |
|---------------------------------------------------------------------------------|------------|------------|------------|------------|
| **Revenue from Operations**                                                     |            |            |            |            |
|   Core Operating Revenue                                                        |            |            |            |            |
|   Other Operating Revenue                                                       |            |            |            |            |
| **Cost of Goods Sold (COGS)**                                                   |            |            |            |            |
|   Raw Material Consumption                                                      |            |            |            |            |
|   Direct Labor Costs                                                            |            |            |            |            |
|   Manufacturing Overhead                                                        |            |            |            |            |
|   Purchase of Traded Goods                                                      |            |            |            |            |
|   Quality Control Costs                                                         |            |            |            |            |
|   Production Supplies                                                           |            |            |            |            |
| **Gross Profit**                                                                |            |            |            |            |
| **Operating Expenses**                                                          |            |            |            |            |
|   Research and Development                                                      |            |            |            |            |   
|   **SG&A**                                                                      |            |            |            |            |
|     Sales and Marketing                                                         |            |            |            |            |
|     General and Administrative                                                  |            |            |            |            |
|   Specialized Operating Costs                                                   |            |            |            |            |
|   Other Operating Expenses                                                      |            |            |            |            |
| **EBITDA**                                                                      |            |            |            |            |
| Depreciation and Amortization Expenses                                          |            |            |            |            |
| **EBIT**                                                                        |            |            |            |            |
| Interest and Dividend Income                                                    |            |            |            |            |
| Interest Expense                                                                |            |            |            |            |
| Other Expenses                                                                  |            |            |            |            |
| **EBT/Profit Before Tax**                                                       |            |            |            |            |
| Taxes                                                                           |            |            |            |            |
| **Profit After Tax**                                                            |            |            |            |            |
| Net Income (Loss) Attributable to Noncontrolling Interest                       |            |            |            |            |
| Net Income Attributable to {company_name}                                       |            |            |            |            |
| **Comprehensive Income**                                                        |            |            |            |            |
| Foreign Currency Translation Gain (Loss)                                        |            |            |            |            |
| Amounts Reclassified from Accumulated OCI to Paid-in Capital                    |            |            |            |            |
| Total Comprehensive Income                                                      |            |            |            |            |
| Net Income (Loss) Attributable to Non-controlling Interest                      |            |            |            |            |
| Foreign Currency Translation Gain (Loss) Attributable to Noncontrolling Interest|            |            |            |            |
| Comprehensive Income Attributable to {company_name}                             |            |            |            |            |
| **Common Shares**                                                               |            |            |            |            |
| **Diluted Shares**                                                              |            |            |            |            |
| Net Income Per Basic Share Attributable to {company_name}                       |            |            |            |            |
| Net Income Per Diluted Share Attributable to {company_name}                     |            |            |            |            |


## Explanations

### Revenue from Operations: 5000.0 (FY{year_2}), 6200.0 (FY{year_4})
Found on Page 2: "Revenue reached $5,000 million for fiscal year ending December {year_2} and $6,200 million for fiscal year ending December {year_4}."
- Fiscal year confirmed as January-December.
- Values converted to millions.
- FY{year_3} data not provided in the document.

### Cost of Goods Sold (COGS): -3000.0 (FY{year_2}), -3700.0 (FY{year_4})
Found on Page 2: "Cost of Goods Sold was -$3,000 million for fiscal year ending December {year_2} and -$3,700 million for fiscal year ending December {year_4}."
- Negative signs preserved as shown in document.
- Values converted to millions.

### Revenue from Operations: 4500.0 (FY{year_2})
Found on Page 3: "Revenue was $4,500 million for fiscal year ending January 31, {year_3}."
- Fiscal year ends in January, so data is mapped to previous year ({year_2}) as it covers mostly {year_2} operations.
- Values converted to millions.

Make sure that the markdown table have all the years from {year_1} to {year_4} without any missing years or extra years.
## Current Income Statement Table
{income_statement_table}

## Previous Explanations
{previous_explanations}

## Similarities
{similarities}

## Current Batch Content
{content}
"""

prompt_balance_sheet = """
# Balance Sheet Data Extraction Instructions

You are tasked with extracting financial data from document pages and filling in a balance sheet markdown table. You will process documents in batches, building upon previously extracted data.

## COMPLETENESS MANDATE
- **Your top priority is to extract every single piece of financial data available in the provided document pages that maps to the line items in the target table for the specified fiscal years ({year_1} through {year_4}).**
- **Be exhaustive in your search. Assume that relevant data might be present anywhere in the text. Do not make assumptions about data absence until all content has been thoroughly reviewed.**
- **If a line item appears in a financial table within the document, even if it's not explicitly named exactly as in our template, use the 'Similarities List' and your financial knowledge to map and extract its values.**
- **When in doubt, extract and explain. It is crucial to capture all potential data points. If a value's exact mapping or interpretation is uncertain, extract the value, place it in the most likely cell, and provide a detailed explanation of your reasoning, confidence level, and any ambiguities in the 'Explanations' section.**

## CRITICAL INSTRUCTIONS
1. **EXTRACT, DON'T CALCULATE VALUES** - Only extract values directly found in the document. Never perform calculations or derive values. If a subtotal or total is not explicitly stated, leave it empty.
2. **PRESERVE NEGATIVE SIGNS** - Preserve any negative signs EXACTLY as they appear in the document. Do not convert negative values to positive or vice versa.
3. **MAINTAIN EXACT TABLE STRUCTURE** - You MUST return the EXACT same markdown table structure as provided in the input, with ALL line items, even if they remain empty. Do not modify, remove, or add rows to the table structure.
4. **CLEAR SECTION SEPARATION** - Ensure your output has a clear separation between the markdown table and the explanations section, using exactly "## Explanations" as the separator.
5. **TARGET TABLES** - Ensure to keep your focus on balance sheet related tables only. Some line items are potentially found in cash flow tables such as inventory. Those values should only be retrieved from balance sheet related tables ONLY.

## Fiscal Year Mapping Rules
- Always map financial data to the exact fiscal year stated in the document.
- CRITICAL: For each value, place it in the column matching the FISCAL YEAR being reported, not the calendar year of the ending date.
- For fiscal periods ending in January, February, or March, data should typically be assigned to the PREVIOUS year:
  - "As of January 31, 2017" → place in {year_3} column (assuming {year_3} is 2016), NOT {year_4} (2017)
  - "Year ended February 28, 2023" → place in 2022 column, NOT 2023
  - "Three months ended March 31, 2020" → place in 2019 column, NOT 2020
- Standard calendar year mappings:
  - "Year ended December 31, {year_3}" belongs in the {year_3} column (NOT {year_2} or {year_4}).
- ALWAYS check the reporting period context - many retailers and companies have fiscal years that don't match the calendar year.
- Watch for explicit fiscal year references like "Fiscal 2021" which directly indicate the correct column.
- If fiscal year timing is unclear, document your reasoning in the explanations.

- Never assume fiscal years match calendar years without confirmation from the document.
- IMPORTANT: Double-check all year mappings before finalizing. A common error is placing data in adjacent year columns.
- Be aware that financial statements may present years in reverse chronological order (newest to oldest). Always map data to the correct year column regardless of presentation order.

## Similarities
You will receive a list of similarities between attributes. Use these similarities to help identify and correctly assign values. For example, if you find "Tangible Capital Assets" in the document, you should assign it to "Net Property, Plant and equipment" in the markdown table, as they are similar concepts.

## Input Format
You will receive:
1. The current batch of document pages.
2. The current state of the balance sheet markdown table (complete, even if only partially filled).
3. Explanations from previous batches (if any).
4. **Similarities List** (to assist in identifying corresponding values).

## Value Population Rules
1. Only populate cells where you have direct evidence from the document.
2. Leave cells empty if:
   - The value isn't explicitly stated.
   - The fiscal year mapping is unclear.
   - You're unsure about the correct year assignment.
   **Only leave cells empty after an exhaustive search of the current batch content. Confirm in explanations if a value is truly absent versus potentially overlooked.**
3. Never:
   - Copy values from one year to another without evidence.
   - Assume continuation of values across years.
   - Infer values based on trends or patterns.
   - Calculate values not explicitly provided in the document.
4. All financial values must be returned in millions of dollars:
   - Convert values accordingly (e.g., "$5 billion" → 5000.0, "$9.576 billion" → 9576.0, "$5,120.350" → 5120.350).
   - Remove extra characters such as "$", "USD", "bn", "billion" before recording.
   - Do not round unnecessarily; preserve the level of detail provided.
5. **Preserve the signs:**  
   - CRITICAL: Maintain ANY negative signs exactly as shown in the source document.
   - Do not assume or "correct" the sign convention.
   - Copy values with their exact sign as displayed in the document.
6. **Fiscal Year Coverage:**
   - IMPORTANT: Thoroughly scan the document for values across ALL fiscal years ({year_1}-{year_4}).
   - Pay special attention to tables or sections showing historical data for earlier years ({year_1}, {year_2}).
   - Look for comparative financial statements that might show multiple years side by side.
   - **Scrutinize financial statement tables, narrative sections, footnotes, MD&A (Management's Discussion and Analysis), and any supplementary schedules or appendices for relevant figures.**
   - Check footnotes and supplementary sections that might contain historical data.
   - If you find ANY value for a fiscal year, ensure it's captured in the table.
   - Document the source location for each year's data in the explanations.

## Output Format
Your response must include exactly two parts with clear separation:
1. **Complete Balance Sheet Markdown Table:**  
   - Include every line item and every fiscal year column, exactly matching the incoming table structure.
   - Even if cells remain unchanged, the complete table must be returned.
   - Do not add or remove rows, even if they remain empty.
   - MANDATORY: You MUST use EXACTLY the same table structure as the input markdown table, preserving all rows and columns. **Ensure all extracted values are placed here.**
2. **Detailed Explanations for Each Value:**  
   - For every updated or newly populated cell, provide:
     - The direct text from the document supporting the value.
     - The page number.
     - The balance sheet date (if mentioned).
     - The fiscal year mapping decision.
     - Any conversion details (e.g., from billions to millions).
     - **If uncertain about a value or its mapping, clearly state your reasoning, confidence, and any ambiguities.**

The two sections must be separated with exactly "## Explanations" on its own line.

## TABLE STRUCTURE TO PRESERVE
You MUST retain EXACTLY the following structure in your response, filling in values based on the principles of completeness outlined above:

| **Line Item**                              | **{year_1}** | **{year_2}** | **{year_3}** | **{year_4}** | 
|--------------------------------------------|------------|------------|------------|------------|
| **Assets**                                 |            |            |            |            | 
|   Cash and Cash Equivalents                |            |            |            |            |  
|   Short-term Investments                   |            |            |            |            |  
|   Accounts Receivables                     |            |            |            |            |  
|   Inventories                              |            |            |            |            |  
|   Prepaid Expenses                         |            |            |            |            |  
|   Deferred Cost (Current)                  |            |            |            |            |  
|   Other Current Assets                     |            |            |            |            |  
|   **Working Capital Assets**               |            |            |            |            |  
|   Long-term Investments                    |            |            |            |            |  
|   Equity Investments                       |            |            |            |            |  
|   Surplus Assets                           |            |            |            |            |  
|   Deferred Cost (Non-Current)              |            |            |            |            |  
|   Other Long-term Assets                   |            |            |            |            |  
|   **Fixed Assets**                         |            |            |            |            |  
|     Net Property, Plant, and Equipment     |            |            |            |            |  
|     ROU Assets                             |            |            |            |            |  
|     Other Intangible Assets                |            |            |            |            |  
|       Trade Names                          |            |            |            |            |  
|     Goodwill                               |            |            |            |            |  
| **Total Assets**                           |            |            |            |            |  
| **Liabilities**                            |            |            |            |            |  
|   **Current Liabilities**                  |            |            |            |            |  
|     Accounts Payable                       |            |            |            |            |  
|     Accrued Payroll                        |            |            |            |            |  
|     Deferred Revenue (Current)             |            |            |            |            |  
|     Income Tax Payables (Current)          |            |            |            |            |  
|     Unearned Revenue (Current)             |            |            |            |            |  
|     Lease Liabilities (Current)            |            |            |            |            |  
|     Other Current Liabilities              |            |            |            |            |  
|   **Total Current Liabilities**            |            |            |            |            |  
|   **Debt & Debt-like Items**               |            |            |            |            |  
|     Short-term Debt                        |            |            |            |            |  
|     Long-term Debt (Current)               |            |            |            |            |  
|     Long-term Debt (Non-Current)           |            |            |            |            |  
|     Other Long-term Liabilities            |            |            |            |            |  
|     Income Tax Payables (Non-Current)      |            |            |            |            |  
|     Lease Liabilities (Non-Current)        |            |            |            |            |  
|     Deferred Revenue (Non-Current)         |            |            |            |            |  
|   **Total Non-Current Liabilities**        |            |            |            |            |  
|   **Convertible Items**                    |            |            |            |            |  
|     Convertible Debt                       |            |            |            |            |  
|     Interest on Convertible Debt           |            |            |            |            |  
|     Preference Shares                      |            |            |            |            |  
|     Interest on Preference Shares          |            |            |            |            |  
| **Total Liabilities**                      |            |            |            |            |  
| **Equity**                                 |            |            |            |            |  
|   Common Stock                             |            |            |            |            |  
|   Paid-in Capital                          |            |            |            |            |  
|   Retained Earnings                        |            |            |            |            |  
|   Accumulated OCI                          |            |            |            |            |  
|   Treasury Stock                           |            |            |            |            |  
|   Non-Controlling Interest                 |            |            |            |            |  
| **Total Equity**                           |            |            |            |            |  
| **Total Equity and Liabilities**           |            |            |            |            |  


## Example Explanations Structure

### Net Property, Plant, and Equipment: 2500.0 (FY{year_2}), 3000.0 (FY{year_4})
Found on Page 3: "Net PP&E was $2,500 million as of December 31, {year_2} and $3,000 million as of December 31, {year_4}."
- Balance sheet dates confirmed.
- Values converted to millions.
- FY{year_3} data not provided in the document.

### Total Assets: 7800.0 (FY{year_2}), 9200.0 (FY{year_3})
Found on Page 3: "Total assets were $7,800 million as of December 31, {year_2} and $9,200 million as of January 31, {year_4}."
- Balance sheet dates confirmed.
- January 31, {year_4} data mapped to {year_3} fiscal year since it represents the {year_3} fiscal year end (majority of the fiscal period occurred in {year_3}).
- Values converted to millions.

### Fixed Assets: 300.0 (FY{year_2}), 370.0 (FY{year_3}), 400.0 (FY{year_4})
Found on Page 5: "Fixed Assets were $300 million for the year ended December 31, {year_2}, $370 million for the year ended December 31, {year_3} and $400 million for the year ended December 31, {year_4}"
- Fiscal year confirmed as January-December.
- Values converted to millions.
- Note: Capital expenditures presented as positive values as shown in document.

Make sure that the markdown table have all the years from {year_1} to {year_4} without any missing years or extra years.
Make sure you don't extract line items from Cash Flow Statement tables as they are don't hold the same values for balance sheet line items.

## Current Balance Sheet Table
{balance_sheet_table}

## Previous Explanations
{previous_explanations}

## Similarities
{similarities}

## Current Batch Content
{content}
"""

attention_prompt = """
# Financial Statement Page Evaluation (Ultra-Strict Filter)

You are a **strict financial statement evaluator**.  
Your job: decide if this page contains a **structured Balance Sheet, Income Statement, or Cash Flow Statement**.  
When uncertain, always return `RETAIN_PAGE: False`.  
False positives are unacceptable.  

---

## Global Header Validity Rule (applies to all statement types)

- A **valid statement header is REQUIRED** on every page.  
- Case-insensitive match.  
- Valid only if header is a **standalone title line** within the first 8 non-empty lines.  
- Acceptable forms:  
  - Exact canonical header (from the statement’s header list).  
  - Same header with “(continued)” appended.  
  - Same header repeated on each page (with or without continued).  
- **No header → reject the page (even if table evidence is strong).**  
- Reject if the header contains **forbidden words**: Condensed, Selected, Summary, Interim, Information, Consolidating (not Consolidated), Supplemental, Extract, Excerpts.  
- Ignore occurrences of statement names in sentences or captions (e.g., “The following table presents the Consolidated Statements of Cash Flows”).  
- If Hard Exclusions fire → reject immediately, header does not count.

- Fallback exception:  
  If the parser fails to mark the header as a standalone line, but the correct statement header text is still clearly present in the **first 8 non-empty lines**, then allow acceptance only if:  
  1. The page contains **exactly one large, structured table** (multi-period, multi-row, units stated).  
  2. No multiple tables, no narrative blocks, no explanatory text beyond footnotes.  
  3. The table itself is **unambiguous** and matches the canonical anchors required for that statement type.  

- In this fallback case, the header must still appear in the first few lines — but being inline with other text does not automatically disqualify it if the table structure and anchors are strong.  
- If there is **any ambiguity** (extra tables, heavy text, captions like “Selected” or “Summary”), reject.  

---

## Table Evidence (after header is confirmed)

- Must contain multi-period columns (“As of …”, “Year ended …”, or explicit dates).  
- Must state units: “(in millions)”, “(in thousands)”, “USD”.  
- Numeric layout: ≥10 numeric tokens across ≥8 labeled rows (exclude captions/footnotes).  
- At least 8 distinct financial line items.  
- Reject tables that are mostly narrative, percentage-only, or KPI dashboards.

---

## Statement-Specific Rules

### A) Balance Sheet
**Header anchors (require ≥1):**  
- Consolidated Balance Sheets  
- Balance Sheet  
- Statement of Financial Position  
- Financial Condition  

**Canonical line anchors (require ≥5 with distribution):**  
- Assets side (≥2): e.g., Cash and cash equivalents, Inventories, Property, plant and equipment, Total assets (strong).  
- Liabilities/Equity side (≥3): e.g., Accounts payable, Long-term debt, Retained earnings, Total liabilities, Total shareholders’ equity (strong).  

**Additional must-have signals:**  
- Must contain both: “Total assets” AND “Total liabilities and (stockholders’|shareholders’) equity”.  
- Assets section must appear above Liabilities & Equity section.  

---

### B) Income Statement
**Header anchors (require ≥1):**  
- Consolidated Statements of Operations  
- Consolidated Statement of Operations  
- Income Statement / Income Statements  
- Consolidated Statements of Profit or Loss  
- Statement of Earnings  
- Profit and Loss  
- Consolidated Income Statements  
- Consolidated Statements of Income  
- Consolidated Statements of Earnings  

**Canonical line anchors (require ≥5, incl. strong anchors):**  
- Examples: Net sales, Gross profit, Operating income, Net income (strong), Earnings per share (strong).  

**Additional must-have signals:**  
- “Net income” (or Net loss).  
- An EPS line (Earnings per share, Basic/Diluted EPS, etc.).  

**Special case:**  
- If both **Income Statement** and **Comprehensive Income** headers appear on the same page, AND the Income Statement rules are satisfied → Accept. (Validator will discard the extra table later.)  

---

### C) Cash Flow Statement
**Header anchors (require ≥1):**  
- Consolidated Statements of Cash Flows  
- Consolidated Statement of Cash Flows  
- Statement of Cash Flows  

**Section anchors (require ≥2):**  
- Net cash provided by operating activities  
- Net cash used in investing activities  
- Net cash used in financing activities  

**Strong anchors (require ≥1):**  
- Net increase in cash  
- Restricted cash  
- Effect of exchange rate changes  
- Cash and cash equivalents at end of period  
- Total cash, cash equivalents, and restricted cash  
- Supplemental non-cash investing and financing activities  
- Supplemental disclosure of cash flow information  

**Accept rule:**  
- Valid header present.  
- Table Evidence satisfied.  
- ≥2 distinct sections (Operating + Investing or Financing).  
- ≥1 strong anchor present.  

**Continuation rule:**  
- If header line contains “(continued)” → Accept if Table Evidence holds.  
- If header is repeated exactly (without continued) → Accept.  
- No header at all → Reject.

---

## Hard Exclusions (absolute)

Reject immediately if any of these appear **anywhere** (title, caption, table box, or embedded section):  
- Condensed  
- Selected (e.g., Selected income statement data, Selected financial data)  
- Summary (e.g., Summary of consolidated statements)  
- Interim  
- Information (when tied to “financial statement” keywords)  
- Consolidating (but not Consolidated)  
- Supplemental (unless part of valid Cash Flow header with evidence)  
- Extract / Excerpts  

Other absolute rejections:  
- “Notes to consolidated financial statements”  
- MD&A, Risk Factors, Certifications, Cover pages, Indexes, Exhibits  
- Statement of changes in shareholders’ equity  
- KPI dashboards, segment breakdowns, Non-GAAP reconciliations  
- Pages mostly narrative or footnotes  
- Index-only pages listing titles/page numbers  

---

## Final Decision Flow

1. Check for valid header (canonical list or canonical + continued).  
   - If missing → Reject.  
   - If forbidden word inside → Reject.  
2. Apply Hard Exclusions.  
   - If triggered → Reject.  
3. Apply Table Evidence.  
   - If failed → Reject.  
4. Apply Canonical line rules per statement type.  
   - If satisfied → Accept (set TYPE).  
   - If failed → Reject.  

---

## Output Format (strict)
RETAIN_PAGE: [True/False]
REASON: [Short explanation citing anchors, table features, and why accepted/rejected]
TYPE: [balance sheet/income statement/cashflow/none]

No extra commentary. Always output exactly in this format.  
---
Here is the page content to evaluate:
<DOCUMENT_CONTENT>
{content}
</DOCUMENT_CONTENT>

"""

evaluator_prompt = """
# Financial Data Extraction Evaluator Instructions

You are an evaluator agent responsible for assessing the accuracy and completeness of financial data extraction. Your role is to verify extracted values against source documents and determine whether to proceed with additional pages or require re-analysis.

## Evaluation Criteria

### 1. Value Classification
For each value in the extraction results, classify it as:
- PREVIOUS_VALUE: Values from previous iterations (marked with sourceIteration < current iteration)
- MISSING_VALUE: Fields with no value that should be present in current pages
- NEW_VALUE: Values extracted from current pages (marked with sourceIteration = current iteration)

### 2. Verification Steps

For PREVIOUS_VALUES:
- No verification needed
- Note their presence in final assessment

For MISSING_VALUES:
- Review current pages thoroughly
- Confirm if values are truly absent or were overlooked
- Flag any overlooked values with page references

For NEW_VALUES:
- Cross-reference against source pages
- Verify numerical accuracy
- Confirm correct context/classification
- Check unit consistency
- Validate confidence levels assigned

### 3. Quality Assessment

Check for:
1. Numerical Accuracy:
   - Direct matches between source and extracted values
   - Correct handling of units/scaling
   - Proper decimal placement

2. Contextual Accuracy:
   - Correct classification of financial items
   - Proper period attribution
   - Appropriate parent category assignment

3. Confidence Level Validity:
   - Justified confidence scores
   - Appropriate preservation of high-confidence values
   - Correct application of update rules

4. Completeness:
   - All available values extracted
   - No overlooked data points
   - Proper handling of nested items

## Required Output Format

Provide your evaluation in this structure:
```
PROCEED: [True/False]

REASON: [Detailed explanation including:
- Summary of verification results
- Specific issues found (if any)
- Recommendations for improvement
- Justification for proceed/reject decision]

DETAILED_FINDINGS:
1. Previous Values: [Count and assessment]
2. Missing Values: [List with page references where applicable]
3. New Values: [Accuracy rate and specific issues]
4. Critical Issues: [Any showstoppers requiring immediate attention]

```
""" 


# Define standard templates
bs_template = """
| **Line Item**                              | **{year_1}** | **{year_2}** | **{year_3}** | **{year_4}** |  
|--------------------------------------------|------------|------------|------------|------------|
| **Assets**                                 |            |            |            |            |  
|   Cash and Cash Equivalents                |            |            |            |            |  
|   Short-term Investments                   |            |            |            |            |  
|   Accounts Receivables                     |            |            |            |            |  
|   Inventories                              |            |            |            |            |  
|   Prepaid Expenses                         |            |            |            |            |  
|   Deferred Cost (Current)                  |            |            |            |            |  
|   Other Current Assets                     |            |            |            |            |  
|   **Working Capital Assets**               |            |            |            |            |  
|   Long-term Investments                    |            |            |            |            |  
|   Equity Investments                       |            |            |            |            |  
|   Surplus Assets                           |            |            |            |            |  
|   Deferred Cost (Non-Current)              |            |            |            |            |  
|   Other Long-term Assets                   |            |            |            |            |  
|   **Fixed Assets**                         |            |            |            |            |  
|     Net Property, Plant, and Equipment     |            |            |            |            |  
|     ROU Assets                             |            |            |            |            |  
|     Other Intangible Assets                |            |            |            |            |  
|       Trade Names                          |            |            |            |            |  
|     Goodwill                               |            |            |            |            |  
| **Total Assets**                           |            |            |            |            |  
| **Liabilities**                            |            |            |            |            |  
|   **Current Liabilities**                  |            |            |            |            |  
|     Accounts Payable                       |            |            |            |            |  
|     Accrued Payroll                        |            |            |            |            |  
|     Deferred Revenue (Current)             |            |            |            |            |  
|     Income Tax Payables (Current)          |            |            |            |            |  
|     Unearned Revenue (Current)             |            |            |            |            |  
|     Lease Liabilities (Current)            |            |            |            |            |  
|     Other Current Liabilities              |            |            |            |            |  
|   **Total Current Liabilities**            |            |            |            |            |  
|   **Debt & Debt-like Items**               |            |            |            |            |  
|     Short-term Debt                        |            |            |            |            |  
|     Long-term Debt (Current)               |            |            |            |            |  
|     Long-term Debt (Non-Current)           |            |            |            |            |  
|     Other Long-term Liabilities            |            |            |            |            |  
|     Income Tax Payables (Non-Current)      |            |            |            |            |  
|     Lease Liabilities (Non-Current)        |            |            |            |            |  
|     Deferred Revenue (Non-Current)         |            |            |            |            |  
|   **Total Non-Current Liabilities**        |            |            |            |            |  
|   **Convertible Items**                    |            |            |            |            |  
|     Convertible Debt                       |            |            |            |            |  
|     Interest on Convertible Debt           |            |            |            |            |  
|     Preference Shares                      |            |            |            |            |  
|     Interest on Preference Shares          |            |            |            |            |  
| **Total Liabilities**                      |            |            |            |            |  
| **Equity**                                 |            |            |            |            |  
|   Common Stock                             |            |            |            |            |  
|   Paid-in Capital                          |            |            |            |            |  
|   Retained Earnings                        |            |            |            |            |  
|   Accumulated OCI                          |            |            |            |            |  
|   Treasury Stock                           |            |            |            |            |  
|   Non-Controlling Interest                 |            |            |            |            |  
| **Total Equity**                           |            |            |            |            |  
| **Total Equity and Liabilities**           |            |            |            |            |  
"""

is_template = """
| **Line Item**                                                                   | **{year_1}** | **{year_2}** | **{year_3}** | **{year_4}** |
|---------------------------------------------------------------------------------|------------|------------|------------|------------|
| **Revenue from Operations**                                                     |            |            |            |            |
|   Core Operating Revenue                                                        |            |            |            |            |
|   Other Operating Revenue                                                       |            |            |            |            |
| **Cost of Goods Sold (COGS)**                                                   |            |            |            |            |
|   Raw Material Consumption                                                      |            |            |            |            |
|   Direct Labor Costs                                                            |            |            |            |            |
|   Manufacturing Overhead                                                        |            |            |            |            |
|   Purchase of Traded Goods                                                      |            |            |            |            |
|   Quality Control Costs                                                         |            |            |            |            |
|   Production Supplies                                                           |            |            |            |            |
| **Gross Profit**                                                                |            |            |            |            |
| **Operating Expenses**                                                          |            |            |            |            |
|   Research and Development                                                      |            |            |            |            |   
|   **SG&A**                                                                      |            |            |            |            |
|     Sales and Marketing                                                         |            |            |            |            |
|     General and Administrative                                                  |            |            |            |            |
|   Specialized Operating Costs                                                   |            |            |            |            |
|   Other Operating Expenses                                                      |            |            |            |            |
| **EBITDA**                                                                      |            |            |            |            |
| Depreciation and Amortization Expenses                                          |            |            |            |            |
| **EBIT**                                                                        |            |            |            |            |
| Interest and Dividend Income                                                    |            |            |            |            |
| Interest Expense                                                                |            |            |            |            |
| Other Expenses                                                                  |            |            |            |            |
| **EBT/Profit Before Tax**                                                       |            |            |            |            |
| Taxes                                                                           |            |            |            |            |
| **Profit After Tax**                                                            |            |            |            |            |
| Net Income (Loss) Attributable to Noncontrolling Interest                       |            |            |            |            |
| Net Income Attributable to {company_name}                                       |            |            |            |            |
| **Comprehensive Income**                                                        |            |            |            |            |
| Foreign Currency Translation Gain (Loss)                                        |            |            |            |            |
| Amounts Reclassified from Accumulated OCI to Paid-in Capital                    |            |            |            |            |
| Total Comprehensive Income                                                      |            |            |            |            |
| Net Income (Loss) Attributable to Non-controlling Interest                      |            |            |            |            |
| Foreign Currency Translation Gain (Loss) Attributable to Noncontrolling Interest|            |            |            |            |
| Comprehensive Income Attributable to {company_name}                             |            |            |            |            |
| **Common Shares**                                                               |            |            |            |            |
| **Diluted Shares**                                                              |            |            |            |            |
| Net Income Per Basic Share Attributable to {company_name}                       |            |            |            |            |
| Net Income Per Diluted Share Attributable to {company_name}                     |            |            |            |            |
""" 

cs_template = """
| **Line Item**                                                   | **year_1** | **year_2** | **year_3** | **year_4** |
|-----------------------------------------------------------------|------------|------------|------------|------------|
| **Net Income**                                                  |            |            |            |            |
| **Adjustments to Reconcile Net Income to Operating Cash Flow**  |            |            |            |            |
|   Depreciation and Amortization                                 |            |            |            |            |
|   Share-Based Compensation Expense                              |            |            |            |            |
|   Payments for Contingent Compensation (Adore Me Acquisition)   |            |            |            |            |
|   Deferred Income Tax                                           |            |            |            |            |
|   Equity Method Investment Impairment Charges                   |            |            |            |            |
|   Gain on Sale of Assets                                        |            |            |            |            |
|   Amortization of Fair Value Adjustment to Acquired Inventories |            |            |            |            |
| **Changes in Working Capital**                                  |            |            |            |            |
|   Accounts Receivable                                           |            |            |            |            |
|   Inventory                                                     |            |            |            |            |
|   Other Current Assets                                          |            |            |            |            |
|   Accounts Payable                                              |            |            |            |            |
|   Accrued Liabilities                                           |            |            |            |            |
|   Income Taxes                                                  |            |            |            |            |
|   Other Current Liabilities                                     |            |            |            |            |
|   Change in Other Liabilities                                   |            |            |            |            |
| **Cash Flow from Operations**                                   |            |            |            |            |
| **Cash Flow from Investing Activities**                         |            |            |            |            |
|   Capital Expenditures                                          |            |            |            |            |
|   Acquisition Net of Cash Acquired                              |            |            |            |            |
|   Change in Other Assets                                        |            |            |            |            |
|   Investment in Frankies Bikinis, LLC                           |            |            |            |            |
|   Asset Dispositions                                            |            |            |            |            |
|   Proceeds from Sale of Assets                                  |            |            |            |            |
|   Other Investing Activities                                    |            |            |            |            |
| **Net Capex**                                                   |            |            |            |            |
|   Additions to PPE                                              |            |            |            |            |
|   Proceeds from Sale of Assets                                  |            |            |            |            |
| **Cash Flow from Investing**                                    |            |            |            |            |
| **Cash Flow from Financing Activities**                         |            |            |            |            |
|   Change in Revolver                                            |            |            |            |            |
|   Repayments of Borrowings (Asset-based Revolving Credit)       |            |            |            |            |
|   Borrowings (Asset-based Revolving Credit)                     |            |            |            |            |
|   Change in Term Loan                                           |            |            |            |            |
|   Payments for Contingent/Deferred Consideration (Adore Me)     |            |            |            |            |
|   Tax Payments (Share-based Awards)                             |            |            |            |            |
|   Proceeds from Stock Option Exercises                          |            |            |            |            |
|   Payments of Long-term Debt                                    |            |            |            |            |
|   Change in Unsecured Debt                                      |            |            |            |            |
|   Cash Received from Non-Controlling Interest Holder            |            |            |            |            |
|   Repurchase of Common Stock                                    |            |            |            |            |
|   Dividends                                                     |            |            |            |            |
|   Other Financing Activities                                    |            |            |            |            |
| **Cash Flow from Financing**                                    |            |            |            |            |
| **Effect of Exchange Rate Changes**                             |            |            |            |            |
| **Net Cash Flow**                                               |            |            |            |            |
| **Cash Before Revolver**                                        |            |            |            |            |
| **Beginning Cash Position**                                     |            |            |            |            |
| **Change in Cash Position**                                     |            |            |            |            |
| **Ending Cash Position**                                        |            |            |            |            |
"""

markdown_cleanup_prompt = """
# Markdown Table Cleanup and Organization

## Task
Your task is to reorganize and clean up a merged markdown table for a financial statement. The merged table may have lost its hierarchical structure, indentation, and proper formatting. Your goal is to restore the original template structure while preserving all the extracted values.

## Input Format
You will receive:
1. A merged markdown table that needs cleanup
2. The financial statement type (either "balance_sheet" or "income_statement" or "cashflow")

## Instructions
1. Analyze the provided markdown table to extract all line items and their values
2. Reorganize the data according to the standard template structure provided below
3. Preserve all numerical values from the input table
4. Maintain proper formatting including:
   - Bold formatting for parent categories/headers
   - Proper indentation for subcategories (using 2 spaces)
   - Consistent column alignment
5. If the merged table contains line items not in the template, add them in an appropriate section

## Expected Output Format
Return ONLY the cleaned and reorganized markdown table, with no additional explanation or commentary.
##### Make sure you use the years that are present in the Current Merged Table (Needs Cleanup) since the bs and is templates are just examples So your task will be to organize and structure the Current Merged Table (Needs Cleanup) into a proper markdown table.

## {statement} Template Structure
{st_template}

## Current Merged Table (Needs Cleanup)
{merged_table}
"""

cashflow_prompt = """
# Cash Flow Statement Data Extraction Instructions

You are tasked with extracting financial data from document pages and filling in a cash flow statement markdown table. You will process documents in batches, building upon previously extracted data.

## CRITICAL INSTRUCTIONS
1. **EXTRACT, DON'T CALCULATE VALUES** - Only extract values directly found in the document. Never perform calculations or derive values. If a subtotal or total is not explicitly stated, leave it empty.
2. **PRESERVE NEGATIVE SIGNS** - Cash outflows are often displayed as negative values in financial statements. Preserve these negative signs EXACTLY as they appear in the document.
3. **MAINTAIN EXACT TABLE STRUCTURE** - You MUST return the EXACT same markdown table structure as provided in the input, with ALL line items, even if they remain empty. Do not modify, remove, or add rows to the table structure.
4. **CLEAR SECTION SEPARATION** - Ensure your output has a clear separation between the markdown table and the explanations section, using exactly "## Explanations" as the separator.

## Fiscal Year Mapping Rules
- Always map financial data to the exact fiscal year stated in the document.
- CRITICAL: For each value, place it in the column matching the FISCAL YEAR being reported, not the calendar year of the ending date.
- For fiscal periods ending in January, February, or March, data should typically be assigned to the PREVIOUS year:
  - "As of January 31, 2017" → place in {year_3} column (assuming {year_3} is 2016), NOT {year_4} (2017)
  - "Year ended February 28, 2023" → place in 2022 column, NOT 2023
  - "Three months ended March 31, 2020" → place in 2019 column, NOT 2020
- Standard calendar year mappings:
  - "Year ended December 31, {year_3}" belongs in the {year_3} column (NOT {year_2} or {year_4}).
- ALWAYS check the reporting period context - many retailers and companies have fiscal years that don't match the calendar year.
- Watch for explicit fiscal year references like "Fiscal 2021" which directly indicate the correct column.
- If fiscal year timing is unclear, document your reasoning in the explanations.

- Never assume fiscal years match calendar years without confirmation from the document.
- IMPORTANT: Double-check all year mappings before finalizing. A common error is placing data in adjacent year columns.
- Be aware that financial statements may present years in reverse chronological order (newest to oldest). Always map data to the correct year column regardless of presentation order.

## Similarities
You will receive a list of similarities between attributes. Use these similarities to help identify and correctly assign values. For example, if you find "Cash from Operations" in the document, you should assign it to "Net Cash Flow from Operating Activities" in the markdown table, as they are similar concepts.

## Input Format
You will receive:
1. The current batch of document pages.
2. The current state of the cash flow statement markdown table (complete, even if only partially filled).
3. Explanations from previous batches (if any).
4. **Similarities List** (to assist in identifying corresponding values).

## Value Population Rules
1. Only populate cells where you have direct evidence from the document.
2. Leave cells empty if:
   - The value isn't explicitly stated.
   - The fiscal year mapping is unclear.
   - You're unsure about the correct year assignment.
3. Never:
   - Copy values from one year to another without evidence.
   - Assume continuation of values across years.
   - Infer values based on trends or patterns.
   - Calculate values not explicitly provided in the document.
4. All financial values must be returned in millions of dollars:
   - Convert values accordingly (e.g., "$5 billion" → 5000.0, "$9.576 billion" → 9576.0, "$5,120.350" → 5120.350).
   - Remove extra characters such as "$", "USD", "bn", "billion" before recording.
   - Do not round unnecessarily; preserve the level of detail provided.
5. **Preserve the signs:**  
   - CRITICAL: Cash outflows MUST maintain their negative signs if presented that way in the document.
   - Many financial statements display outflows with negative signs (e.g., "-$500 million" for capital expenditures).
   - Copy the sign EXACTLY as shown in the source document.
   - Do not assume or "correct" the sign convention.
6. **Fiscal Year Coverage:**
   - IMPORTANT: Thoroughly scan the document for values across ALL fiscal years ({year_1}-{year_4}).
   - Pay special attention to tables or sections showing historical data for earlier years ({year_1}, {year_2}).
   - Look for comparative financial statements that might show multiple years side by side.
   - Check footnotes and supplementary sections that might contain historical data.
   - If you find ANY value for a fiscal year, ensure it's captured in the table.
   - Document the source location for each year's data in the explanations.

## Output Format
Your response must include exactly two parts with clear separation:
1. **Complete Cash Flow Statement Markdown Table:**  
   - Include every line item and every fiscal year column, exactly matching the incoming table structure.
   - Even if cells remain unchanged, the complete table must be returned.
   - Do not add or remove rows, even if they remain empty.
   - MANDATORY: You MUST use EXACTLY the same table structure as the input markdown table, preserving all rows and columns.
2. **Detailed Explanations for Each Value:**  
   - For every updated or newly populated cell, provide:
     - The direct text from the document supporting the value.
     - The page number.
     - The fiscal period end date (if mentioned).
     - The fiscal year mapping decision.
     - Any conversion details (e.g., from billions to millions).

The two sections must be separated with exactly "## Explanations" on its own line.

## TABLE STRUCTURE TO PRESERVE
You MUST retain EXACTLY the following structure in your response, filling in values only where you have direct evidence:

| **Line Item**                                                   | **year_1** | **year_2** | **year_3** | **year_4** |
|-----------------------------------------------------------------|------------|------------|------------|------------|
| **Net Income**                                                  |            |            |            |            |
| **Adjustments to Reconcile Net Income to Operating Cash Flow**  |            |            |            |            |
|   Depreciation and Amortization                                 |            |            |            |            |
|   Share-Based Compensation Expense                              |            |            |            |            |
|   Payments for Contingent Compensation (Adore Me Acquisition)   |            |            |            |            |
|   Deferred Income Tax                                           |            |            |            |            |
|   Equity Method Investment Impairment Charges                   |            |            |            |            |
|   Gain on Sale of Assets                                        |            |            |            |            |
|   Amortization of Fair Value Adjustment to Acquired Inventories |            |            |            |            |
| **Changes in Working Capital**                                  |            |            |            |            |
|   Accounts Receivable                                           |            |            |            |            |
|   Inventory                                                     |            |            |            |            |
|   Other Current Assets                                          |            |            |            |            |
|   Accounts Payable                                              |            |            |            |            |
|   Accrued Liabilities                                           |            |            |            |            |
|   Income Taxes                                                  |            |            |            |            |
|   Other Current Liabilities                                     |            |            |            |            |
|   Change in Other Liabilities                                   |            |            |            |            |
| **Cash Flow from Operations**                                   |            |            |            |            |
| **Cash Flow from Investing Activities**                         |            |            |            |            |
|   Capital Expenditures                                          |            |            |            |            |
|   Acquisition Net of Cash Acquired                              |            |            |            |            |
|   Change in Other Assets                                        |            |            |            |            |
|   Investment in Frankies Bikinis, LLC                           |            |            |            |            |
|   Asset Dispositions                                            |            |            |            |            |
|   Proceeds from Sale of Assets                                  |            |            |            |            |
|   Other Investing Activities                                    |            |            |            |            |
| **Net Capex**                                                   |            |            |            |            |
|   Additions to PPE                                              |            |            |            |            |
|   Proceeds from Sale of Assets                                  |            |            |            |            |
| **Cash Flow from Investing**                                    |            |            |            |            |
| **Cash Flow from Financing Activities**                         |            |            |            |            |
|   Change in Revolver                                            |            |            |            |            |
|   Repayments of Borrowings (Asset-based Revolving Credit)       |            |            |            |            |
|   Borrowings (Asset-based Revolving Credit)                     |            |            |            |            |
|   Change in Term Loan                                           |            |            |            |            |
|   Payments for Contingent/Deferred Consideration (Adore Me)     |            |            |            |            |
|   Tax Payments (Share-based Awards)                             |            |            |            |            |
|   Proceeds from Stock Option Exercises                          |            |            |            |            |
|   Payments of Long-term Debt                                    |            |            |            |            |
|   Change in Unsecured Debt                                      |            |            |            |            |
|   Cash Received from Non-Controlling Interest Holder            |            |            |            |            |
|   Repurchase of Common Stock                                    |            |            |            |            |
|   Dividends                                                     |            |            |            |            |
|   Other Financing Activities                                    |            |            |            |            |
| **Cash Flow from Financing**                                    |            |            |            |            |
| **Effect of Exchange Rate Changes**                             |            |            |            |            |
| **Net Cash Flow**                                               |            |            |            |            |
| **Cash Before Revolver**                                        |            |            |            |            |
| **Beginning Cash Position**                                     |            |            |            |            |
| **Change in Cash Position**                                     |            |            |            |            |
| **Ending Cash Position**                                        |            |            |            |            |

## Example of Explanations Structure

### Net Cash Flow from Operating Activities: 800.0 (FY{year_2}), 950.0 (FY{year_4})
Found on Page 3: "Cash flow from operations totaled $800 million for fiscal year ending December {year_2} and $950 million for fiscal year ending December {year_4}."
- Fiscal year confirmed as January-December.
- Values converted to millions.
- FY{year_3} data not provided in the document.

### Capital Expenditures: -450.0 (FY{year_2}), -520.0 (FY{year_4})
Found on Page 3: "Capital expenditures were -$450 million for fiscal year ending December {year_2} and -$520 million for fiscal year ending December {year_4}."
- Negative signs preserved as shown in document.
- Values converted to millions.

### Cash from Operations: 780.0 (FY{year_3})
Found on Page 4: "Cash from operations was $780 million for year ended January 28, {year_4}."
- Fiscal year ends in January, so data is mapped to previous year ({year_3}) as it covers mostly {year_3} operations.
- Values converted to millions.

Make sure that the markdown table have all the years from {year_1} to {year_4} without any missing years or extra years.
## Current Cash Flow Statement Table
{cashflow_table}

## Previous Explanations
{previous_explanations}

## Similarities
{similarities}

## Current Batch Content
{content}
"""




attention_prompt2 = """
# Financial Statement Page Evaluation (High-Precision Filter)

You are a strict financial statement evaluator. Your task is to decide if the page contains a **structured** Balance Sheet, Income Statement, or Cash Flow Statement suitable for extraction. Be **conservative**: when uncertain, return RETAIN_PAGE: False.

Global header validity rule (applies to A/B/C):
- Case-insensitive matching.
- Treat a header as valid only if it appears as a standalone title line within the first 8 non-empty lines on the page (no preceding sentence/caption on the same line).
- Ignore occurrences of statement names that appear inside sentences or captions, such as lines beginning with "The following table ...", "The following tables ...", "Selected financial data ...", "Reconciliation ...", "Key metrics ...".
- A line is NOT a valid header if it contains preceding punctuation on the same line (e.g., ":" or "-"), such as "The following tables present: Consolidated Statements of Cash Flows ...". A header must be an isolated title line.
- If the top-of-page context screen (see Hard Exclusions) triggers, then no line on this page can be treated as a valid statement header, even if it exactly matches a header phrase.

## Table Evidence (must meet **all** below)
- Multi-period columns: e.g., "As of", "Year ended", or explicit dates like "September 30, 2024".
- Units indicated: "(in millions)", "(in thousands)", "USD", etc.
- Numeric layout: at least 10 numeric tokens across >=8 labeled rows (exclude footnotes and caption rows).
- Multiple labeled lines: at least 8 distinct financial line items (exclude footnotes, caption lines like "The following table ...", and percent-only rows).
- When counting labeled rows/lines, do not count caption/schedule identifiers such as "supplemental ...", "related to leases", "supplier/vendor financing", "additional financial information", "the following tables ...".
- Do not accept pages that only reference statements without presenting numeric tables (e.g., indexes).

---

## A) Balance Sheet
### Header anchors (need >=1, exact match required; case-insensitive):
- "Consolidated Balance Sheets"
- "Consolidated Financial Position"
- "Balance Sheet"
- "Statement of Financial Position"
- "Financial Condition"
(Apply the Global header validity rule.)

### Canonical line anchors (need >=5 with distribution):
- Assets (need >=2): e.g., "Cash and cash equivalents", "Inventories", "Property, plant and equipment", "Total assets" (strong)
- Liabilities/Equity (need >=3): e.g., "Accounts payable", "Long-term debt", "Retained earnings", "Total liabilities", "Total shareholders' equity" (strong)

Accept rule: Table Evidence + >=1 Header + >=5 Canonical lines (with required split) + >=1 Strong Total

Additional must-have signals (same page):
- "Total assets" AND "Total liabilities and (stockholders'|shareholders') equity" must both be present.
- Ordering check: The "Assets" section appears above the "Liabilities and (stockholders'|shareholders') equity" section.

---

## B) Income Statement
### Header anchors (need >=1, exact match required; case-insensitive):
- "Consolidated Statements of Operations"
- "Consolidated Statement of Operations"
- "Consolidated Results of Operations"
- "Income Statement"
- "Income Statements"
- "Consolidated statements of profit or loss"
- "Statement of Earnings"
- "Profit and Loss"
- "Consolidated Income statements"
- "Consolidated statements of Income"
- "Consolidated Statements of Earnings"
- "Statement of Comprehensive Income"
- "Statements of Comprehensive Income"
- "Consolidated Statement of Comprehensive Income"
- "Consolidated Statements of Comprehensive Income"
(Apply the Global header validity rule.)

### Canonical line anchors (need >=5 total):
- e.g., "Net sales", "Gross profit", "Operating income", "Net income" (strong), "Earnings per share" (strong), etc.

Accept rule: Table Evidence + >=1 Header + >=5 Canonical lines + >=1 Strong Anchor

Additional must-have signals (same page):
- "Net income" (or "Net loss"), AND
- an EPS line, e.g., "Earnings per share" (basic or diluted), or equivalent phrasing such as "Basic/Diluted net income per share".

---

## C) Cash Flow Statement
### Header anchors (need >=1, exact match required; case-insensitive):
- "Consolidated Statements of Cash Flows"
- "Statement of Cash Flows"
(Apply the Global header validity rule.)

### Section anchors (need >=2 of; exact-match only):
- "Net cash provided by operating activities"
- "Net cash used in investing activities"
- "Net cash used in financing activities"
(Do NOT treat similar phrasing like "Cash flows from operating activities" or "Operating cash flows from leases" as equal to the exact phrases above.)

If none of the exact anchors are found, accept soft equivalents if at least two distinct **activity blocks** are detected. Soft equivalents include:
- "Cash flows from operating activities"
- "Operating cash flow"
- "Investing activities"
- "Financing activities"
- "Cash provided by financing"
- "Cash used in investing"

Soft match rule applies only if:
- Table Evidence is fully satisfied
- At least one strong anchor (e.g., "Net increase in cash") is also present


### Additional strong anchor (need >=1):
- "Net increase in cash", "Restricted cash", "Effect of exchange rate changes"

Accept rule: Table Evidence + >=1 Header + >=2 Sections + >=1 Strong Anchor

Additional must-have signals (on the SAME PAGE; any one of these suffices alongside the sections above):
- "Net cash provided by operating activities" AND one of:
  - "Cash and cash equivalents at end of (period|year)", or
  - "Total cash, cash equivalents, and restricted cash" at end, or
  - "Net increase (decrease) in cash".

---
## Continuations If the page has "(continued)" and carries forward a known statement, retain it if Table Evidence holds and >=5 canonical lines for that type are present, even without a fresh header.
 
Continuation guardrails:
 - "(continued)" must appear on a statement title line within the first 8 non-empty lines (apply the Global header validity rule).
 - Ignore "(continued)" that appears only in captions, notes, or schedule headings. 
 - Presence of a statement name inside a caption (e.g., "The following tables present ... Consolidated ...") does NOT make the page a continuation; only a title line with "(continued)" qualifies.
 - For valid continuation pages, the "Additional must-have signals" listed above do not need to be on the continuation page itself. 
 - "CONSOLIDATED BALANCE SHEETS (continued)" or "Consolidated Statements of Cash Flows (Continued)" or "Consolidated Statements of Operations (Continued)" this will be considered continuations (case insensitive).The page just before must have passed either one of the A/B/C rules.
 - "CONSOLIDATED BALANCE SHEETS (continued)" 
 - or "Consolidated Statements of Cash Flows (Continued)" 
 - or "Consolidated Statements of Operations (Continued)" 
 - or "Consolidated Statements of Comprehensive Income (Continued)" 
 - will be considered continuations (case insensitive). 
 - The page just before must have passed either one of the A/B/C rules.
---

## Hard Exclusions (RETAIN_PAGE: False, no matter what)
- "Notes to consolidated financial statements"
- MD&A, risk factors, certifications, cover pages, indexes, exhibits
- "Statement of changes in shareholders' equity"
- KPI dashboards, segment breakdowns, non-GAAP reconciliations
- Pages with mostly narrative or footnotes
- Capital expenditure tables alone (e.g., "Additions to PPE") do not qualify a page.
- Index pages listing titles and page numbers of financial statements, without actual tables or numeric data, must be excluded.
- Any page where the statement header/title line contains the word "Condensed" 
  (e.g., "Condensed Consolidated Balance Sheets", "Condensed Statements of Earnings", 
  "Condensed Statements of Cash Flows", etc.) must be rejected, regardless of 
  table evidence, continuation status, or canonical line matches.
- If "Statement of comprehensive income" appears, treat it as a valid Income Statement header 
- (apply the same Table Evidence + canonical line checks as Rule B).
- If BOTH Income Statement and Comprehensive Income headers appear on the SAME PAGE and 
  Income Statement passes Table Evidence + canonical line checks → accept as income statement.

Top-of-page context screen (first 15 non-empty lines, case-insensitive):
- If any of these phrases appear -> RETAIN_PAGE: False. No exceptions.
  "NOTE ", "Notes", "Additional financial information", "Supplemental",
  "supplemental cash flow", "lease disclosures", "related to leases",
  "supplier financing", "vendor financing", "The following table",
  "The following tables", "The following is a summary", "Non-GAAP",
  "Management's Discussion and Analysis", "Results of Operations",
  "Selected financial data", "Schedule of" , "cash flows summary","ANALYSIS OF THE CONSOLIDATED STATEMENTS OF CASH FLOWS, "cash flows were as follows"

---

## Final Decision Logic
All required headers, anchors, and must-have signals must appear on THIS PAGE ONLY. Do not infer from adjacent pages or prior pages. Continuations are allowed only per the explicit "(continued)" title rule.

Return RETAIN_PAGE: True only if:
1) All Table Evidence criteria are satisfied
2) One of the A/B/C rules is fully satisfied
3) No Hard Exclusions are present

If the REASON supports inclusion, RETAIN_PAGE must be True. If there is doubt, err on the side of False.

---
## Type Field
Add a third output field TYPE to identify the statement kind.
Allowed values: balance sheet | income statement | cashflow | none.

If RETAIN_PAGE is True:
- TYPE must be one of balance sheet, income statement, or cashflow, determined by which acceptance rule (A/B/C) is satisfied:

- Rule A satisfied ⇒ balance sheet

- Rule B satisfied ⇒ income statement

- Rule C satisfied ⇒ cashflow

- For valid continuation pages, TYPE must match the continued statement’s type.

If RETAIN_PAGE is False: TYPE must be none.
---

## Output format (no extra text)
RETAIN_PAGE: [True/False]
REASON: [Short explanation citing anchors, table features, and why it was accepted or rejected.]
TYPE: [balance sheet/income statement/cashflow/none]

*Always respond with both RETAIN_PAGE and REASON exactly as shown — no other formatting or summary.*

---

Here is the page content to evaluate:
<DOCUMENT_CONTENT>
{content}
</DOCUMENT_CONTENT>


"""