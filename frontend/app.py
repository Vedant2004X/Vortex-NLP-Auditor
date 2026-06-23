"""
ProtocolAudit — Document Redliner Frontend (Fixed)
Run: streamlit run frontend/app.py
"""

import json
import os
import io
import requests
import streamlit as st
import streamlit.components.v1 as components

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="ProtocolAudit",
    page_icon="⚑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #0F1117 !important;
    color: #F7F4EE !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #0F1117; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }
div[data-testid="stToolbar"] { display: none; }
[data-testid="stFileUploader"] {
    background: #252836 !important;
    border: 1px dashed #3A3D4A !important;
    border-radius: 8px !important;
    padding: 8px !important;
}
[data-testid="stFileUploader"] label { color: #9DA4B4 !important; font-size: 13px !important; }
.stButton > button {
    background: #E8C84A !important;
    color: #0F1117 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 28px !important;
    width: 100% !important;
    margin-top: 8px !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sample data (fallback / demo mode) ───────────────────────────────────────

SAMPLE_PROTOCOL = {
    "title": "PROT-2024-417 — Phase III Randomised Controlled Trial of XR-441 in Treatment-Resistant Major Depressive Disorder",
    "version": "v3.2",
    "date": "14 March 2024",
    "sections": [
        {
            "id": "s1",
            "heading": "1. Study Objectives",
            "paragraphs": [
                {
                    "id": "p1",
                    "text": "The primary objective of this study is to evaluate the efficacy and safety of XR-441 administered at doses of 10 mg, 25 mg, and 50 mg once daily for 12 weeks in adult patients with treatment-resistant major depressive disorder (TR-MDD), as defined by failure to respond to at least two adequate antidepressant trials.",
                    "spans": []
                },
                {
                    "id": "p2",
                    "text": "Secondary objectives include assessment of quality of life using the PHQ-9 scale at weeks 4, 8, and 12, evaluation of the time to first response, and measurement of remission rates at endpoint. Biomarker sub-studies will assess serum BDNF levels and inflammatory cytokine profiles.",
                    "spans": [
                        {"start": 46, "end": 170, "violation_id": "V001", "type": "citation", "severity": "warning", "label": "PHQ-9 — version not cited"}
                    ]
                }
            ]
        },
        {
            "id": "s2",
            "heading": "2. Eligibility Criteria",
            "paragraphs": [
                {
                    "id": "p3",
                    "text": "Inclusion criteria: Adults aged 18–65 years with a confirmed DSM-5 diagnosis of major depressive disorder, MADRS total score ≥ 28 at screening, and documented failure of at least two prior antidepressants at adequate doses and duration.",
                    "spans": [
                        {"start": 20, "end": 113, "violation_id": "V002", "type": "critical", "severity": "critical", "label": "Age range conflicts with FDA IND"}
                    ]
                },
                {
                    "id": "p4",
                    "text": "Exclusion criteria: Active suicidal ideation (C-SSRS score ≥ 4), current or recent (within 6 months) diagnosis of bipolar I or II disorder, psychotic disorder, substance use disorder, or borderline personality disorder. Patients with hepatic impairment (Child-Pugh B or C) are excluded without exception.",
                    "spans": [
                        {"start": 220, "end": 305, "violation_id": "V003", "type": "guideline", "severity": "warning", "label": "Hepatic clause missing washout period"}
                    ]
                },
                {
                    "id": "p5",
                    "text": "Female participants of childbearing potential must use two forms of contraception throughout the study and for 90 days following the last dose. Male participants with partners of childbearing potential must use barrier contraception.",
                    "spans": []
                }
            ]
        },
        {
            "id": "s3",
            "heading": "3. Study Design & Randomisation",
            "paragraphs": [
                {
                    "id": "p6",
                    "text": "This is a double-blind, placebo-controlled, parallel-group study. Eligible participants will be randomised 1:1:1:1 to receive XR-441 10 mg, XR-441 25 mg, XR-441 50 mg, or matched placebo once daily for 12 weeks. Randomisation will be stratified by site and baseline MADRS severity (moderate: 28–34; severe: ≥ 35).",
                    "spans": []
                },
                {
                    "id": "p7",
                    "text": "The primary endpoint is change from baseline in MADRS total score at week 12. All assessments will be performed by trained and certified raters who are blinded to treatment allocation. An independent Data Safety Monitoring Board (DSMB) will conduct pre-specified interim analyses at 25% and 75% enrolment.",
                    "spans": [
                        {"start": 24, "end": 76, "violation_id": "V004", "type": "citation", "severity": "info", "label": "MADRS — version not specified"}
                    ]
                },
                {
                    "id": "p8",
                    "text": "Dose adjustments are not permitted during the double-blind phase. In the event of intolerability, the investigator may temporarily suspend dosing for up to 7 days before permanent discontinuation. Rescue medication with benzodiazepines is permitted at the investigator's discretion.",
                    "spans": [
                        {"start": 197, "end": 280, "violation_id": "V005", "type": "critical", "severity": "critical", "label": "Rescue med clause undermines blinding"}
                    ]
                }
            ]
        },
        {
            "id": "s4",
            "heading": "4. Statistical Analysis Plan",
            "paragraphs": [
                {
                    "id": "p9",
                    "text": "The primary efficacy analysis will be conducted in the Full Analysis Set (FAS) using a mixed-effects model for repeated measures (MMRM) with treatment, visit, treatment-by-visit interaction, baseline MADRS, and stratification factors as covariates.",
                    "spans": []
                },
                {
                    "id": "p10",
                    "text": "A sample size of 320 participants (80 per arm) provides 90% power to detect a difference of 4.5 MADRS points between each active dose and placebo, assuming a standard deviation of 10.5 and a two-sided alpha of 0.05. This calculation does not account for multiplicity across the three dose comparisons.",
                    "spans": [
                        {"start": 224, "end": 300, "violation_id": "V006", "type": "critical", "severity": "critical", "label": "Missing multiplicity correction — ICH E9 violation"}
                    ]
                },
                {
                    "id": "p11",
                    "text": "All secondary endpoints will be analysed using appropriate statistical tests. Missing data will be handled using multiple imputation under a missing-at-random assumption. Sensitivity analyses will explore alternative missing data assumptions.",
                    "spans": [
                        {"start": 78, "end": 168, "violation_id": "V007", "type": "guideline", "severity": "warning", "label": "MAR assumption requires pre-specification"}
                    ]
                }
            ]
        }
    ]
}

SAMPLE_VIOLATIONS = {
    "V001": {
        "id": "V001", "type": "citation", "severity": "warning",
        "title": "PHQ-9 — Instrument version not cited",
        "section": "1. Study Objectives",
        "excerpt": "Secondary objectives include assessment of quality of life using the PHQ-9 scale at weeks 4, 8, and 12…",
        "issue": "PHQ-9 is referenced as a secondary outcome measure but neither the validated version nor the language adaptation is specified. Regulatory guidance (EMA/CHMP/SAWP) requires explicit citation of the instrument version and any linguistic validation documentation.",
        "guideline": "ICH E6(R2) §6.4.1; EMA Reflection Paper on PRO Measures (2014)",
        "recommendation": "Specify: PHQ-9 (Kroenke & Spitzer, 2001), English version. Attach linguistic validation report if non-English sites are included.",
        "citations_found": [], "status": "open"
    },
    "V002": {
        "id": "V002", "type": "critical", "severity": "critical",
        "title": "Age ceiling conflicts with IND filing",
        "section": "2. Eligibility Criteria",
        "excerpt": "Adults aged 18–65 years with a confirmed DSM-5 diagnosis of major depressive disorder, MADRS total score ≥ 28 at screening…",
        "issue": "The approved IND (reference IND-0091724) specifies an age range of 18–60 years for Phase III studies with XR-441, based on PK data indicating altered clearance in the 60–65 cohort. The current protocol upper limit of 65 years is inconsistent with the IND and PK bridging study findings.",
        "guideline": "FDA IND-0091724 §3.2; XR-441 PK Bridging Report (March 2023)",
        "recommendation": "Revert upper age limit to 60 years OR submit IND amendment with supporting PK data before protocol finalisation.",
        "citations_found": ["XR-441 Investigator Brochure v7 §4.3"], "status": "open"
    },
    "V003": {
        "id": "V003", "type": "guideline", "severity": "warning",
        "title": "Hepatic exclusion missing washout specification",
        "section": "2. Eligibility Criteria",
        "excerpt": "Patients with hepatic impairment (Child-Pugh B or C) are excluded without exception.",
        "issue": "The exclusion criterion for hepatic impairment does not specify whether participants with a prior history of Child-Pugh B/C who have since recovered are also excluded. This ambiguity could lead to inconsistent site-level eligibility decisions.",
        "guideline": "ICH E6(R2) §4.3; FDA Guidance for Industry: Hepatic Impairment Studies (2020)",
        "recommendation": "Clarify: 'Current or historical Child-Pugh B or C hepatic impairment within the past [X] months.' Consult hepatology consultant for appropriate lookback window.",
        "citations_found": [], "status": "open"
    },
    "V004": {
        "id": "V004", "type": "citation", "severity": "info",
        "title": "MADRS version not specified",
        "section": "3. Study Design & Randomisation",
        "excerpt": "change from baseline in MADRS total score at week 12.",
        "issue": "MADRS is cited as the primary endpoint instrument but the specific version and administration format is not specified.",
        "guideline": "EMA Guideline on Clinical Investigation of Medicinal Products in MDD (2013)",
        "recommendation": "Specify: 'Montgomery–Åsberg Depression Rating Scale (MADRS; Montgomery & Åsberg, 1979), administered via the Structured Interview Guide (SIGMA).'",
        "citations_found": ["Montgomery SA, Åsberg M. Br J Psychiatry. 1979"], "status": "open"
    },
    "V005": {
        "id": "V005", "type": "critical", "severity": "critical",
        "title": "Rescue benzodiazepine clause threatens blind integrity",
        "section": "3. Study Design & Randomisation",
        "excerpt": "Rescue medication with benzodiazepines is permitted at the investigator's discretion.",
        "issue": "Permitting open-label benzodiazepine rescue without a structured recording and analysis framework threatens the integrity of the double-blind design.",
        "guideline": "ICH E9 §5.7; FDA Guidance on Adaptive Design (2019) §IV.B",
        "recommendation": "1. Cap benzodiazepine use: no more than 3 doses per participant per week, lorazepam ≤2 mg equivalent. 2. Require logging in eCRF. 3. Include rescue use as a covariate in sensitivity analysis.",
        "citations_found": [], "status": "open"
    },
    "V006": {
        "id": "V006", "type": "critical", "severity": "critical",
        "title": "Missing multiplicity correction — ICH E9 violation",
        "section": "4. Statistical Analysis Plan",
        "excerpt": "This calculation does not account for multiplicity across the three dose comparisons.",
        "issue": "The SAP explicitly acknowledges no multiplicity correction is applied across three primary dose-vs-placebo comparisons. This is a direct violation of ICH E9 §5.6.",
        "guideline": "ICH E9 §5.6; FDA Multiple Endpoints Guidance (2022)",
        "recommendation": "Apply a hierarchical testing procedure (e.g., fixed-sequence: 50 mg → 25 mg → 10 mg) or Hochberg correction.",
        "citations_found": [], "status": "open"
    },
    "V007": {
        "id": "V007", "type": "guideline", "severity": "warning",
        "title": "MAR assumption requires pre-specification and justification",
        "section": "4. Statistical Analysis Plan",
        "excerpt": "Missing data will be handled using multiple imputation under a missing-at-random assumption.",
        "issue": "The missing-at-random (MAR) assumption is stated without clinical justification. In psychiatric trials, dropout is frequently related to treatment response or side effects.",
        "guideline": "NRC Panel on Handling Missing Data (2010); EMA Guideline on Missing Data (2010)",
        "recommendation": "Add clinical justification for MAR assumption. Pre-specify MNAR sensitivity analyses: tipping point analysis and pattern-mixture model.",
        "citations_found": [], "status": "open"
    }
}


# ── API helpers ───────────────────────────────────────────────────────────────

def api_upload_protocol(file_bytes: bytes, filename: str) -> dict | None:
    """Upload PDF to /upload-protocol, return JSON or None on error."""
    try:
        resp = requests.post(
            f"{API_BASE}/upload-protocol",
            files={"file": (filename, io.BytesIO(file_bytes), "application/pdf")},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.session_state.api_error = str(e)
        return None


def api_run_audit(document_id: str) -> dict | None:
    """POST /audit with the document_id, return JSON or None on error."""
    try:
        resp = requests.post(
            f"{API_BASE}/audit",
            json={"protocol_document_id": document_id},
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.session_state.api_error = str(e)
        return None


# ── Convert API AuditReport → viewer format ──────────────────────────────────

_SEVERITY_MAP = {
    "critical": "critical",
    "major": "critical",
    "minor": "warning",
    "observation": "info",
}

_STATUS_TYPE_MAP = {
    "violation": "critical",
    "omission": "guideline",
    "needs_review": "guideline",
    "compliant": "citation",
}


def _finding_to_violation(f: dict, vid: str) -> dict:
    stmt = f.get("statement", {})
    sev = _SEVERITY_MAP.get(f.get("severity", "minor"), "warning")
    typ = _STATUS_TYPE_MAP.get(f.get("status", "needs_review"), "guideline")
    text = stmt.get("text", "")
    excerpt = (text[:120] + "…") if len(text) > 120 else text
    citations = [
        c.get("cited_clause_id", "")
        for c in f.get("citation_checks", [])
        if c.get("citation_found_in_guideline")
    ]
    guideline_refs = "; ".join(
        cl.get("clause_id", "") for cl in f.get("matched_clauses", [])
    ) or "See attached guideline"

    return {
        "id": vid,
        "type": typ,
        "severity": sev,
        "title": f.get("explanation", "Issue detected")[:80],
        "section": f"{stmt.get('section_number', '')} {stmt.get('section_title', '')}".strip() or "Unknown section",
        "excerpt": excerpt,
        "issue": f.get("explanation", ""),
        "guideline": guideline_refs,
        "recommendation": f.get("suggested_correction", "Review and correct per referenced guideline."),
        "citations_found": citations,
        "status": "open",
    }


def audit_report_to_viewer(report: dict, filename: str) -> tuple[dict, dict]:
    """
    Convert AuditReport JSON → (protocol_dict, violations_dict) for the HTML viewer.
    Groups findings by section and builds paragraph spans that highlight the FULL statement.
    """
    findings = report.get("findings", [])
    # Group findings by section
    sections_map: dict[str, list] = {}
    for f in findings:
        stmt = f.get("statement", {})
        sec_key = f"{stmt.get('section_number', '')}|{stmt.get('section_title', '')}".strip("|")
        sections_map.setdefault(sec_key, []).append(f)

    sections = []
    violations = {}
    vid_counter = 1

    for sec_key, sec_findings in sections_map.items():
        parts = sec_key.split("|", 1)
        sec_num = parts[0].strip() if parts else ""
        sec_title = parts[1].strip() if len(parts) > 1 else ""
        heading = f"{sec_num}. {sec_title}".strip(". ") if sec_num else sec_title or "General"

        paragraphs = []
        for f in sec_findings:
            stmt = f.get("statement", {})
            text = stmt.get("text", "")
            if not text:
                continue

            # Only flag non-compliant findings
            if f.get("status") == "compliant":
                paragraphs.append({"id": stmt.get("statement_id", "p"), "text": text, "spans": []})
                continue

            vid = f"V{vid_counter:03d}"
            vid_counter += 1
            violations[vid] = _finding_to_violation(f, vid)

            # Highlight the ENTIRE statement text as a span
            span = {
                "start": 0,
                "end": len(text),
                "violation_id": vid,
                "type": violations[vid]["type"],
                "severity": violations[vid]["severity"],
                "label": violations[vid]["title"][:50],
            }
            paragraphs.append({"id": stmt.get("statement_id", "p"), "text": text, "spans": [span]})

        if paragraphs:
            sections.append({
                "id": sec_key,
                "heading": heading,
                "paragraphs": paragraphs,
            })

    if not sections:
        # Fallback: flat dump of all findings
        paragraphs = []
        for f in findings:
            stmt = f.get("statement", {})
            text = stmt.get("text", "")
            if not text:
                continue
            if f.get("status") == "compliant":
                paragraphs.append({"id": stmt.get("statement_id", "p"), "text": text, "spans": []})
                continue
            vid = f"V{vid_counter:03d}"
            vid_counter += 1
            violations[vid] = _finding_to_violation(f, vid)
            span = {"start": 0, "end": len(text), "violation_id": vid,
                    "type": violations[vid]["type"], "severity": violations[vid]["severity"],
                    "label": violations[vid]["title"][:50]}
            paragraphs.append({"id": stmt.get("statement_id", "p"), "text": text, "spans": [span]})
        sections = [{"id": "s_all", "heading": "Protocol Statements", "paragraphs": paragraphs}]

    protocol = {
        "title": report.get("source_document_name", filename),
        "version": "",
        "date": report.get("created_at", "")[:10] if report.get("created_at") else "",
        "sections": sections,
    }
    return protocol, violations


# ── HTML viewer builder ───────────────────────────────────────────────────────

def build_app_html(filename: str, protocol: dict, violations: dict) -> str:
    protocol_json = json.dumps(protocol)
    violations_json = json.dumps(violations)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>ProtocolAudit</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --ink: #0F1117; --paper: #F7F4EE; --paper-dim: #EDE9E0;
    --chrome: #1A1D27; --chrome-border: #2A2D3A; --chrome-mid: #252836;
    --text-muted: #6B7080; --text-dim: #9DA4B4;
    --amber: #E8C84A; --amber-bg: rgba(232,200,74,0.12); --amber-border: rgba(232,200,74,0.35);
    --red: #F05252; --red-bg: rgba(240,82,82,0.10); --red-border: rgba(240,82,82,0.35);
    --blue: #5B8DEF; --blue-bg: rgba(91,141,239,0.10); --blue-border: rgba(91,141,239,0.30);
    --green: #3DBD7D; --panel-w: 420px;
  }}
  html, body {{ height: 100%; }}
  body {{ background: var(--ink); color: var(--paper); font-family: 'Inter', sans-serif; font-size: 14px; line-height: 1.6; overflow: hidden; }}
  #topbar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 100;
    height: 52px; background: var(--chrome); border-bottom: 1px solid var(--chrome-border);
    display: flex; align-items: center; padding: 0 24px; gap: 0;
  }}
  .tb-brand {{ display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 600; letter-spacing: 0.04em; color: var(--paper); margin-right: 32px; }}
  .tb-brand .dot {{ width: 8px; height: 8px; background: var(--amber); border-radius: 50%; }}
  .tb-meta {{ flex: 1; font-size: 12px; color: var(--text-dim); overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
  .tb-meta strong {{ color: var(--paper); font-weight: 500; }}
  .tb-stats {{ display: flex; align-items: center; gap: 4px; flex-shrink: 0; }}
  .stat-pill {{ display: flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 500; letter-spacing: 0.02em; }}
  .stat-pill.critical {{ background: var(--red-bg); border: 1px solid var(--red-border); color: var(--red); }}
  .stat-pill.warning {{ background: var(--amber-bg); border: 1px solid var(--amber-border); color: var(--amber); }}
  .stat-pill.info {{ background: var(--blue-bg); border: 1px solid var(--blue-border); color: var(--blue); }}
  .stat-pill .pill-num {{ font-size: 14px; font-weight: 600; }}
  .stat-sep {{ width: 1px; height: 20px; background: var(--chrome-border); margin: 0 8px; }}
  .tb-action {{ margin-left: 16px; padding: 6px 16px; background: var(--amber); border: none; border-radius: 6px; color: var(--ink); font-size: 12px; font-weight: 600; cursor: pointer; transition: opacity 0.15s; }}
  .tb-action:hover {{ opacity: 0.85; }}
  #layout {{ position: fixed; top: 52px; bottom: 0; left: 0; right: 0; display: flex; }}
  #doc-pane {{ flex: 1; overflow-y: auto; background: var(--ink); }}
  #doc-inner {{ max-width: 740px; margin: 0 auto; padding: 40px 48px 80px; }}
  .doc-title {{ font-family: 'DM Mono', monospace; font-size: 13px; font-weight: 500; color: var(--text-muted); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 4px; }}
  .doc-heading {{ font-size: 20px; font-weight: 600; color: var(--paper); line-height: 1.3; margin-bottom: 4px; }}
  .doc-version {{ font-family: 'DM Mono', monospace; font-size: 11px; color: var(--text-dim); margin-bottom: 40px; }}
  .doc-divider {{ height: 1px; background: var(--chrome-border); margin: 32px 0; }}
  .section-heading {{ font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 500; color: var(--text-muted); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 14px; }}
  .para {{ font-family: 'DM Mono', monospace; font-size: 13.5px; font-weight: 300; line-height: 1.85; color: #C8C4BC; margin-bottom: 18px; }}
  .vmark {{ position: relative; cursor: pointer; border-radius: 2px; padding: 1px 0; transition: all 0.12s ease; }}
  .vmark.critical {{ background: var(--red-bg); border-bottom: 2px solid var(--red); color: #F7C4C4; }}
  .vmark.warning {{ background: var(--amber-bg); border-bottom: 2px solid var(--amber); color: #F2E4B0; }}
  .vmark.info {{ background: var(--blue-bg); border-bottom: 2px solid var(--blue); color: #B3C9F5; }}
  .vmark:hover {{ filter: brightness(1.25); }}
  .vmark.active {{ outline: 1px solid currentColor; outline-offset: 1px; }}
  .vmark-tag {{ display: inline-flex; align-items: center; gap: 3px; font-size: 9px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; vertical-align: middle; margin-left: 3px; padding: 1px 5px; border-radius: 3px; opacity: 0.9; }}
  .critical .vmark-tag {{ background: var(--red); color: white; }}
  .warning .vmark-tag {{ background: var(--amber); color: var(--ink); }}
  .info .vmark-tag {{ background: var(--blue); color: white; }}
  #side-panel {{ width: 0; overflow: hidden; background: var(--chrome); border-left: 1px solid var(--chrome-border); transition: width 0.3s cubic-bezier(0.4,0,0.2,1); flex-shrink: 0; display: flex; flex-direction: column; }}
  #side-panel.open {{ width: var(--panel-w); }}
  #panel-inner {{ width: var(--panel-w); overflow-y: auto; flex: 1; padding: 24px; }}
  .panel-close {{ position: sticky; top: 0; display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; z-index: 10; }}
  .panel-close-btn {{ background: none; border: 1px solid var(--chrome-border); color: var(--text-dim); width: 28px; height: 28px; border-radius: 6px; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; transition: all 0.12s; }}
  .panel-close-btn:hover {{ background: var(--chrome-mid); color: var(--paper); }}
  .panel-vid {{ font-family: 'DM Mono', monospace; font-size: 10px; color: var(--text-dim); letter-spacing: 0.1em; }}
  .panel-severity-badge {{ display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 4px; font-size: 10px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 12px; }}
  .panel-severity-badge.critical {{ background: var(--red-bg); border: 1px solid var(--red-border); color: var(--red); }}
  .panel-severity-badge.warning {{ background: var(--amber-bg); border: 1px solid var(--amber-border); color: var(--amber); }}
  .panel-severity-badge.info {{ background: var(--blue-bg); border: 1px solid var(--blue-border); color: var(--blue); }}
  .panel-title {{ font-size: 16px; font-weight: 600; color: var(--paper); line-height: 1.4; margin-bottom: 16px; }}
  .panel-excerpt {{ font-family: 'DM Mono', monospace; font-size: 11.5px; font-style: italic; color: var(--text-dim); border-left: 2px solid var(--chrome-border); padding: 10px 14px; margin-bottom: 20px; line-height: 1.7; border-radius: 0 4px 4px 0; }}
  .panel-section-label {{ font-size: 10px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px; margin-top: 18px; }}
  .panel-issue {{ font-size: 13px; color: #B0ADA6; line-height: 1.75; margin-bottom: 2px; }}
  .panel-guideline {{ display: flex; align-items: flex-start; gap: 8px; padding: 10px 12px; background: var(--chrome-mid); border: 1px solid var(--chrome-border); border-radius: 6px; font-family: 'DM Mono', monospace; font-size: 11px; color: var(--text-dim); line-height: 1.6; }}
  .panel-recommendation {{ font-size: 13px; color: #B0ADA6; line-height: 1.75; }}
  .panel-divider {{ height: 1px; background: var(--chrome-border); margin: 20px 0; }}
  .panel-citations {{ display: flex; flex-direction: column; gap: 6px; }}
  .citation-pill {{ display: flex; align-items: center; gap: 8px; padding: 6px 10px; background: rgba(61,189,125,0.08); border: 1px solid rgba(61,189,125,0.25); border-radius: 5px; font-family: 'DM Mono', monospace; font-size: 11px; color: #7FD4AA; }}
  .citation-empty {{ font-family: 'DM Mono', monospace; font-size: 11px; color: var(--text-muted); font-style: italic; }}
  .panel-resolve-btn {{ width: 100%; margin-top: 24px; padding: 10px; background: none; border: 1px solid var(--chrome-border); border-radius: 6px; color: var(--text-dim); font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.12s; letter-spacing: 0.02em; }}
  .panel-resolve-btn:hover {{ background: var(--chrome-mid); color: var(--paper); border-color: rgba(255,255,255,0.15); }}
  #hint-state {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 32px; text-align: center; color: var(--text-muted); gap: 12px; }}
  .hint-icon {{ font-size: 32px; opacity: 0.3; }}
  .hint-text {{ font-size: 13px; line-height: 1.6; max-width: 260px; }}
  #progress-overlay {{ position: fixed; inset: 0; background: rgba(15,17,23,0.97); z-index: 200; display: flex; align-items: center; justify-content: center; }}
  .progress-box {{ display: flex; flex-direction: column; align-items: center; gap: 20px; width: 340px; }}
  .progress-label {{ font-family: 'DM Mono', monospace; font-size: 12px; color: var(--text-dim); letter-spacing: 0.06em; text-transform: uppercase; min-height: 18px; }}
  .progress-bar-track {{ width: 100%; height: 2px; background: var(--chrome-border); border-radius: 2px; overflow: hidden; }}
  .progress-bar-fill {{ height: 100%; background: var(--amber); width: 0%; transition: width 0.4s ease; border-radius: 2px; }}
  .progress-title {{ font-size: 16px; font-weight: 600; color: var(--paper); text-align: center; }}
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
  ::-webkit-scrollbar-thumb {{ background: var(--chrome-border); border-radius: 3px; }}
</style>
</head>
<body>
<div id="progress-overlay">
  <div class="progress-box">
    <div class="progress-title" id="progress-title-text">Auditing: {filename}</div>
    <div class="progress-bar-track"><div class="progress-bar-fill" id="prog-fill"></div></div>
    <div class="progress-label" id="prog-label">Initialising…</div>
  </div>
</div>
<div id="topbar">
  <div class="tb-brand"><div class="dot"></div>PROTOCOLAUDIT</div>
  <div class="tb-meta">
    <strong id="tb-doc-title">—</strong>
    <span id="tb-doc-meta" style="margin-left:12px;"></span>
  </div>
  <div class="tb-stats">
    <div class="stat-pill critical"><span class="pill-num" id="stat-critical">0</span> Critical</div>
    <div class="stat-sep"></div>
    <div class="stat-pill warning"><span class="pill-num" id="stat-warning">0</span> Warnings</div>
    <div class="stat-sep"></div>
    <div class="stat-pill info"><span class="pill-num" id="stat-info">0</span> Citations</div>
    <button class="tb-action" onclick="exportReport()">Export Report</button>
  </div>
</div>
<div id="layout">
  <div id="doc-pane">
    <div id="doc-inner"></div>
  </div>
  <div id="side-panel">
    <div id="panel-inner">
      <div id="hint-state">
        <div class="hint-icon">↖</div>
        <div class="hint-text">Click any highlighted passage to see the violation detail and recommended remediation.</div>
      </div>
      <div id="panel-content" style="display:none;"></div>
    </div>
  </div>
</div>
<script>
const PROTOCOL = {protocol_json};
const VIOLATIONS = {violations_json};
const UPLOADED_FILENAME = "{filename}";
let activeViolationId = null;

window.addEventListener('load', function() {{
  const steps = [
    [8,  'Reading PDF structure…'],
    [20, 'Extracting protocol statements…'],
    [35, 'Loading guideline index…'],
    [50, 'Running semantic retrieval…'],
    [63, 'Verifying citations…'],
    [75, 'Classifying violations with LLM…'],
    [88, 'Scoring severity levels…'],
    [95, 'Generating audit report…'],
    [100,'Complete ✓'],
  ];
  let i = 0;
  function tick() {{
    if (i >= steps.length) {{
      setTimeout(() => {{
        document.getElementById('progress-overlay').style.display = 'none';
        renderDocument();
      }}, 500);
      return;
    }}
    const [pct, label] = steps[i++];
    document.getElementById('prog-fill').style.width = pct + '%';
    document.getElementById('prog-label').textContent = label;
    setTimeout(tick, 400 + Math.random() * 200);
  }}
  setTimeout(tick, 300);
}});

function renderDocument() {{
  const prot = PROTOCOL;
  document.getElementById('tb-doc-title').textContent = prot.title || UPLOADED_FILENAME;
  const meta = [prot.version, prot.date].filter(Boolean).join(' · ');
  document.getElementById('tb-doc-meta').textContent = meta;

  const viols = Object.values(VIOLATIONS);
  document.getElementById('stat-critical').textContent = viols.filter(v => v.severity === 'critical').length;
  document.getElementById('stat-warning').textContent = viols.filter(v => v.severity === 'warning').length;
  document.getElementById('stat-info').textContent = viols.filter(v => v.severity === 'info').length;

  let html = '';
  html += `<div class="doc-title">Clinical Trial Protocol</div>`;
  html += `<div class="doc-heading">${{escHtml(prot.title || UPLOADED_FILENAME)}}</div>`;
  if (meta) html += `<div class="doc-version">${{escHtml(meta)}}</div>`;

  prot.sections.forEach((section, si) => {{
    if (si > 0) html += '<div class="doc-divider"></div>';
    html += `<div class="section-heading">${{escHtml(section.heading)}}</div>`;
    section.paragraphs.forEach(para => {{
      html += `<p class="para">${{buildParagraph(para)}}</p>`;
    }});
  }});

  document.getElementById('doc-inner').innerHTML = html;
  document.querySelectorAll('.vmark').forEach(el => {{
    el.addEventListener('click', (e) => {{
      e.stopPropagation();
      openPanel(el.dataset.vid);
    }});
  }});
  document.getElementById('doc-pane').addEventListener('click', () => closePanel());
}}

function buildParagraph(para) {{
  if (!para.spans || para.spans.length === 0) return escHtml(para.text);
  const spans = [...para.spans].sort((a, b) => a.start - b.start);
  let result = '';
  let cursor = 0;
  spans.forEach(span => {{
    if (span.start > cursor) result += escHtml(para.text.substring(cursor, span.start));
    const spanText = escHtml(para.text.substring(span.start, span.end));
    const typeLabel = span.severity === 'critical' ? 'CRITICAL' : span.severity === 'warning' ? 'WARN' : 'CITE';
    result += `<span class="vmark ${{span.severity}}" data-vid="${{span.violation_id}}" title="${{escAttr(span.label)}}">`;
    result += spanText;
    result += `<span class="vmark-tag">${{typeLabel}}</span></span>`;
    cursor = span.end;
  }});
  if (cursor < para.text.length) result += escHtml(para.text.substring(cursor));
  return result;
}}

function escHtml(s) {{ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}
function escAttr(s) {{ return String(s||'').replace(/"/g,'&quot;'); }}

function openPanel(vid) {{
  const v = VIOLATIONS[vid];
  if (!v) return;
  document.querySelectorAll('.vmark.active').forEach(el => el.classList.remove('active'));
  document.querySelectorAll(`.vmark[data-vid="${{vid}}"]`).forEach(el => el.classList.add('active'));
  activeViolationId = vid;

  const citationHtml = v.citations_found && v.citations_found.length
    ? v.citations_found.map(c => `<div class="citation-pill">✓ ${{escHtml(c)}}</div>`).join('')
    : `<div class="citation-empty">No supporting citations found in document</div>`;

  const typeLabel = v.severity === 'critical' ? 'Critical Issue' : v.type === 'guideline' ? 'Guideline Deviation' : 'Citation Required';

  document.getElementById('panel-content').innerHTML = `
    <div class="panel-close">
      <span class="panel-vid">${{v.id}}</span>
      <button class="panel-close-btn" onclick="closePanel()">✕</button>
    </div>
    <div class="panel-severity-badge ${{v.severity}}">${{typeLabel}}</div>
    <div class="panel-title">${{escHtml(v.title)}}</div>
    <div class="panel-excerpt">&ldquo;${{escHtml(v.excerpt)}}&rdquo;</div>
    <div class="panel-section-label">Issue</div>
    <div class="panel-issue">${{escHtml(v.issue)}}</div>
    <div class="panel-section-label">Guideline Reference</div>
    <div class="panel-guideline">${{escHtml(v.guideline)}}</div>
    <div class="panel-section-label">Recommendation</div>
    <div class="panel-recommendation">${{escHtml(v.recommendation)}}</div>
    <div class="panel-divider"></div>
    <div class="panel-section-label">Citations Found in Document</div>
    <div class="panel-citations">${{citationHtml}}</div>
    <button class="panel-resolve-btn" onclick="resolveViolation('${{vid}}')">Mark as Resolved ↗</button>
  `;
  document.getElementById('hint-state').style.display = 'none';
  document.getElementById('panel-content').style.display = 'block';
  document.getElementById('side-panel').classList.add('open');
}}

function closePanel() {{
  document.querySelectorAll('.vmark.active').forEach(el => el.classList.remove('active'));
  activeViolationId = null;
  document.getElementById('side-panel').classList.remove('open');
  document.getElementById('hint-state').style.display = 'flex';
  document.getElementById('panel-content').style.display = 'none';
}}

function resolveViolation(vid) {{
  document.querySelectorAll(`.vmark[data-vid="${{vid}}"]`).forEach(mark => {{
    mark.style.opacity = '0.3';
    mark.style.textDecoration = 'line-through';
    mark.style.pointerEvents = 'none';
  }});
  const v = VIOLATIONS[vid];
  if (v) {{
    const key = v.severity === 'critical' ? 'stat-critical' : v.severity === 'warning' ? 'stat-warning' : 'stat-info';
    const el = document.getElementById(key);
    if (el) el.textContent = Math.max(0, parseInt(el.textContent) - 1);
  }}
  closePanel();
}}

function exportReport() {{
  const viols = Object.values(VIOLATIONS);
  let report = "PROTOCOL AUDIT REPORT\\n";
  report += "=".repeat(50) + "\\n";
  report += "Document: " + (PROTOCOL.title || UPLOADED_FILENAME) + "\\n";
  report += "Version: " + (PROTOCOL.version || '') + " | " + (PROTOCOL.date || '') + "\\n";
  report += "=".repeat(50) + "\\n\\n";
  report += "SUMMARY\\n-------\\n";
  report += "Critical Issues: " + viols.filter(v => v.severity === 'critical').length + "\\n";
  report += "Warnings: " + viols.filter(v => v.severity === 'warning').length + "\\n";
  report += "Citation Issues: " + viols.filter(v => v.severity === 'info').length + "\\n\\n";
  viols.forEach(v => {{
    report += "-".repeat(50) + "\\n";
    report += "[" + v.id + "] " + v.severity.toUpperCase() + " — " + v.title + "\\n";
    report += "Section: " + v.section + "\\n";
    report += "Excerpt: " + v.excerpt + "\\n\\n";
    report += "ISSUE:\\n" + v.issue + "\\n\\n";
    report += "GUIDELINE: " + v.guideline + "\\n\\n";
    report += "RECOMMENDATION:\\n" + v.recommendation + "\\n\\n";
  }});
  const blob = new Blob([report], {{type: 'text/plain'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'audit_report_' + UPLOADED_FILENAME.replace(/[^a-z0-9]/gi,'_') + '.txt';
  a.click();
}}
</script>
</body>
</html>"""
    return html


# ── Main app ──────────────────────────────────────────────────────────────────

def main():
    # Session state init
    if "loaded" not in st.session_state:
        st.session_state.loaded = False
    if "filename" not in st.session_state:
        st.session_state.filename = None
    if "protocol" not in st.session_state:
        st.session_state.protocol = None
    if "violations" not in st.session_state:
        st.session_state.violations = None
    if "api_error" not in st.session_state:
        st.session_state.api_error = None
    # BUG FIX: use a keyed uploader so we can force-reset it
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    if not st.session_state.loaded:
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:center;min-height:80vh;">
        <div style="background:#1A1D27;border:1px solid #2A2D3A;border-radius:12px;
        padding:48px 56px;max-width:480px;width:100%;text-align:center;">
        <div style="font-size:40px;margin-bottom:16px;">⚑</div>
        <div style="font-size:22px;font-weight:600;color:#F7F4EE;margin-bottom:8px;">Protocol Auditor</div>
        <div style="font-size:13px;color:#9DA4B4;line-height:1.7;margin-bottom:28px;">
        Upload a clinical trial protocol PDF. The AI will identify guideline violations,
        missing citations, and structural issues — highlighted inline in the document.</div>
        </div></div>
        """, unsafe_allow_html=True)

        # BUG FIX: use dynamic key so widget fully resets on new upload session
        uploaded = st.file_uploader(
            "Upload Protocol PDF",
            type=["pdf"],
            label_visibility="collapsed",
            key=f"uploader_{st.session_state.uploader_key}",
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            demo = st.button("Load sample protocol →", use_container_width=True)

        if uploaded:
            file_bytes = uploaded.read()
            fname = uploaded.name

            with st.spinner("Uploading and analysing protocol…"):
                upload_resp = api_upload_protocol(file_bytes, fname)

            if upload_resp is None:
                # API not reachable — show error but still let sample load
                st.error(
                    f"⚠️ Backend API not reachable at `{API_BASE}`. "
                    "Make sure `uvicorn app.main:app` is running. "
                    "Showing sample data for UI preview instead."
                )
                st.session_state.protocol = SAMPLE_PROTOCOL
                st.session_state.violations = SAMPLE_VIOLATIONS
                st.session_state.filename = fname
                st.session_state.loaded = True
                st.rerun()
            else:
                doc_id = upload_resp.get("document_id")
                with st.spinner("Running AI audit against embedded guidelines…"):
                    audit_resp = api_run_audit(doc_id)

                if audit_resp is None:
                    st.error(
                        f"⚠️ Audit failed: {st.session_state.api_error}. "
                        "Showing sample data instead."
                    )
                    st.session_state.protocol = SAMPLE_PROTOCOL
                    st.session_state.violations = SAMPLE_VIOLATIONS
                else:
                    protocol, violations = audit_report_to_viewer(audit_resp, fname)
                    st.session_state.protocol = protocol
                    st.session_state.violations = violations

                st.session_state.filename = fname
                st.session_state.loaded = True
                st.rerun()

        if demo:
            st.session_state.protocol = SAMPLE_PROTOCOL
            st.session_state.violations = SAMPLE_VIOLATIONS
            st.session_state.filename = "PROT-2024-417_XR441.pdf"
            st.session_state.loaded = True
            st.rerun()

    else:
        fname = st.session_state.filename or "protocol.pdf"
        protocol = st.session_state.protocol or SAMPLE_PROTOCOL
        violations = st.session_state.violations or SAMPLE_VIOLATIONS

        html = build_app_html(fname, protocol, violations)
        components.html(html, height=920, scrolling=False)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("← Upload New Protocol"):
            # BUG FIX: clear ALL state and increment uploader key to force widget reset
            st.session_state.loaded = False
            st.session_state.filename = None
            st.session_state.protocol = None
            st.session_state.violations = None
            st.session_state.api_error = None
            st.session_state.uploader_key += 1
            st.rerun()


if __name__ == "__main__":
    main()