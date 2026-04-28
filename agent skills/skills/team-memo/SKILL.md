---
name: team-memo
description: Use this skill when creating, revising, or verifying the Milestone 4 team memo for the capstone project. This includes drafting the 5-7 page final investment memo, aligning it with the Milestone 4 PDF requirements, using results/tables, results/figures, and results/reports from the repository, and generating a professional PDF focused on cross-asset divergence. Trigger when the user asks for the team memo, final investment memo, Milestone 4 memo, or a report based on the Milestone 4 instructions.
---

# Team Memo Skill

## Purpose
Create a professional Milestone 4 memo that translates the capstone analysis into a concise, decision-oriented PDF for a non-technical audience.

## When to Use
Use this skill when the task is to:
- Draft or revise the final team memo for Milestone 4
- Summarize findings from M1, M2, and M3 into one report
- Turn the analysis into a 5-7 page professional PDF
- Ensure the memo focuses on divergence across asset classes, not just individual asset returns

## Required Inputs
Before writing the memo, gather the following from the repository:
- The Milestone 4 PDF instructions
- The latest M1 data quality or pipeline summary
- The M2 EDA summary
- The M3 interpretation memo
- The final regression tables and robustness tables in `results/tables/`
- Relevant figures in `results/figures/`
- The data dictionary in `data/final/`

## Core Workflow
1. Read the Milestone 4 instructions carefully and extract the required sections and page-length target.
2. Confirm the research question is cross-asset divergence, not only asset-level return prediction.
3. Pull the key numbers from the repository outputs:
   - sample size and date range
   - main fixed effects coefficient(s)
   - robustness checks
   - diagnostics and key figure references
4. Write the memo in clear business language with no unexplained jargon.
5. Build the memo around the required structure:
   - Executive Summary
   - Methodology
   - Results
   - Conclusions & Recommendations
   - References
   - AI Audit appendix
6. Keep the report within 5-7 pages when rendered to PDF.
7. Produce a polished PDF with professional typography, readable tables, and figure references.

## Content Rules
- Focus on divergence between asset classes and the factors that widen or compress it.
- Use only verified numbers from repository outputs; do not invent coefficients, p-values, or sample sizes.
- Translate statistical results into economic implications for a portfolio manager or investment committee.
- State limitations honestly, including omitted variables, external validity, and modeling assumptions.
- Avoid all-caps section headers, markdown artifacts, and raw console output in the final PDF.
- Ensure recommendations are specific and actionable, not vague.

## Section Guidance
### Executive Summary
- 2-3 sentences on the main finding
- 1-2 sentences on the investment or portfolio recommendation
- No tables or figures

### Methodology
- Data sources with citations
- Sample construction: assets, months, and date range
- Model equations and variable definitions
- Explanation of fixed effects and any alternative specifications

### Results
- Main regression table
- Alternative specification or robustness table
- Key visual and diagnostic figure references
- Plain-language interpretation of the coefficients

### Conclusions & Recommendations
- Buy/hold/sell or overweight/underweight guidance where appropriate
- Risk assessment and caveats
- Honest discussion of what could go wrong

### References
- Data source URLs
- Any academic or methodological references used
- Use a professional citation style

### AI Audit
- Disclose AI use across milestones
- Include verification and critique examples

## Quality Checks
Before finishing, verify that:
- The memo matches the Milestone 4 instructions
- The PDF is 5-7 pages
- The memo is readable by a non-technical audience
- The report clearly states the divergence research question
- Tables and figures match repository outputs
- The final file is a PDF, not a Word doc

## Common Mistakes to Avoid
- Reverting to asset-level analysis when the project question is divergence
- Copying raw statistical output without interpretation
- Overly long prose that pushes the PDF beyond 7 pages
- Using markdown symbols or all-caps styling in the rendered PDF
- Making recommendations not supported by the analysis
