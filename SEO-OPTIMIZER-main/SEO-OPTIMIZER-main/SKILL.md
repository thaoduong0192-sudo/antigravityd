---
name: seo-analyzer
description: Use this skill when the user asks to audit, analyze, score, or improve
  the SEO of a web page, landing page, or website. Activated by phrases like "analyze SEO", "check SEO score", "improve ranking", "audit my page", "otimizar SEO", or "auditoria SEO".
---

# SEO Analyzer & Score Improver

## Goal
Perform a complete SEO audit on a given URL or local HTML file, generate
a numeric score (0–100) broken into 5 weighted categories, and produce
a prioritized action plan with ready-to-apply fixes in the user's preferred language (English or Portuguese).

---

## Instructions

### Phase 1 — Language & Target Collection
1. **Detect Language**: Detect if the user is communicating in **English** or **Portuguese**. Use `--lang en` for English and `--lang pt` for Portuguese in subsequent script calls.
2. Ask the user for the **URL or local file path** of the page to be audited, if not provided.
3. Ask if they want a **quick audit** (metadata + content, ~2 min) or a **full audit** (including Core Web Vitals via PageSpeed API, ~5 min).
4. If a PageSpeed audit is requested, ask for the optional **Google PageSpeed API key** (or proceed without it using Lighthouse CLI).

### Phase 2 — Run the Audit Scripts
Execute the scripts in order. Do NOT skip steps.

**Step 2a — Technical & On-Page Scrape**
```bash
python scripts/seo_audit.py "<URL_OR_FILE>"
```

**Step 2b — Core Web Vitals (Full Audit only)**
```bash
python scripts/core_web_vitals.py "<URL>"
```

### Phase 3 — Score & Generate Report
After collecting the JSON outputs, run the report generator with the appropriate language flag.

**Step 3 — Generate Final Report**
```bash
python scripts/generate_report.py "<JSON_AUDIT>" ["<JSON_VITALS>"] --lang <en|pt>
```

### Phase 4 — Apply Fixes (Optional)
If the user asks to apply fixes to a **local file**:
- Apply only the changes explicitly listed in the audit report.
- Make a backup of the original file as `<filename>.seo-backup` before editing.
- After editing, re-run the audit and report the updated score delta. If the language is Portuguese, say something like "Score melhorado de 61 → 78 ✅".

---

## Constraints
- **Language Consistency**: If the user asks in Portuguese, all responses and reports must be in Portuguese. If in English, all in English.
- NEVER guess or hallucinate tag values. Only report what the scripts return.
- NEVER apply fixes to a remote/production URL. Local files only.
- If no API key is provided for PageSpeed, skip Core Web Vitals and calculate the final score over 80 total points.

---

## Examples

**Example 1 — Quick Audit (English)**
User: "Analyze the SEO of https://mysite.com"
Agent: 
1. Runs `seo_audit.py`
2. Runs `generate_report.py ... --lang en`
3. Responds in English.

**Example 2 — Auditoria (Português)**
Usuário: "Analisa o SEO de https://meusite.com.br"
Agente:
1. Executa `seo_audit.py`
2. Executa `generate_report.py ... --lang pt`
3. Responde em Português.

