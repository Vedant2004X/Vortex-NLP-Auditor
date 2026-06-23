[README (2).md](https://github.com/user-attachments/files/29230895/README.2.md)
# ⚑ Vortex-NLP — AI Regulatory Compliance Auditor

> Built at **Ethosh IGNITE 2026 Hackathon** · FastAPI · Ollama · FAISS · Streamlit

Vortex-NLP is a **100% local, privacy-first AI system** that reads your regulatory guidelines, scans your clinical documents, and instantly flags every compliance violation — highlighted inline, with exact guideline references and fix recommendations.

No cloud. No API fees. No data leaves your machine.

---

## The Problem

Regulatory compliance auditing in pharma and medtech is done manually by expensive consultants reading thousands of pages. A single Clinical Evaluation Report audit takes weeks and costs tens of thousands of dollars. One missed citation or age-range conflict with an IND filing can delay a drug approval by months.

## Our Solution

Vortex-NLP automates the entire pipeline in minutes:

1. Upload your protocol or CER document (PDF)
2. The system parses it into semantic statement units
3. Each statement is retrieved against a pre-indexed regulatory guideline (ICH E6, MDR 2017/745, FDA guidance) using FAISS vector search
4. A local LLM (Llama 3.1 via Ollama) reasons about each statement and classifies it as compliant, violation, omission, or needs review
5. Results are rendered as an interactive redlined document — click any highlight to see the violation, guideline reference, and recommended fix

---

## Why This Is Different

| Feature | Vortex-NLP | GPT-4 / Cloud APIs |
|---|---|---|
| Data privacy | ✅ 100% local, never leaves server | ❌ Sent to external servers |
| API cost | ✅ $0 — runs on your hardware | ❌ $10–100+ per audit |
| Offline capability | ✅ Full air-gap support | ❌ Requires internet |
| Guideline grounding | ✅ FAISS retrieval over actual guidelines | ❌ Hallucinated references |
| Inline redlining UI | ✅ Click-to-inspect violation panel | ❌ Chat-style output |
| Citation verification | ✅ Cross-checks self-citations in document | ❌ Not available |

---

## Tech Stack

```
Backend          FastAPI + Uvicorn
PDF Parsing      PyMuPDF (fitz)
Embeddings       SentenceTransformers (all-MiniLM-L6-v2)
Vector Search    FAISS (facebook/faiss-cpu)
LLM Reasoning    Llama 3.1 8B via Ollama (fully local)
Database         SQLite + SQLAlchemy
Frontend         Streamlit + custom HTML/CSS/JS redliner UI
```

---

## Architecture

```
PDF Upload
    │
    ▼
PyMuPDF Parser ──► Statement Chunker ──► SQLite Store
                                              │
                                              ▼
                              FAISS Retriever (guideline index)
                                              │
                                              ▼
                              Ollama LLM Reasoner (Llama 3.1)
                                              │
                                              ▼
                              Report Builder ──► Streamlit Redliner UI
```

---

## Features

- **Inline redlined document viewer** — violations highlighted directly in document text, colour-coded by severity (Critical / Warning / Citation)
- **Click-to-inspect panel** — each highlight opens a detail panel with the exact guideline clause, issue explanation, and fix recommendation
- **Severity scoring** — Critical, Major, Minor, Observation
- **Citation cross-checker** — verifies that citations made inside the document actually exist in the guideline
- **Export audit report** — download a structured `.txt` audit report
- **Mark as Resolved** — interactively resolve violations in the UI
- **Pre-built guideline index** — ICH E6(R2), MDR 2017/745 indexed and ready; no setup needed

---

## Quickstart

### Prerequisites
- Python 3.12+
- [Ollama](https://ollama.ai) installed and running
- Llama 3.1 pulled: `ollama pull llama3.1:8b`

### Run

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/Vortex-NLP.git
cd Vortex-NLP

# Install
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Terminal 1 — Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
streamlit run frontend/app.py
```

Open `http://localhost:8501`

---

## Project Structure

```
Vortex-NLP/
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── config.py
│   ├── db/                      # SQLAlchemy models + session
│   ├── routers/
│   │   ├── upload.py            # /upload-protocol, /upload-guideline
│   │   └── audit.py             # /audit
│   ├── schemas/
│   │   └── audit.py             # Pydantic contracts
│   └── services/
│       ├── pdf_parser.py        # PyMuPDF statement extraction
│       ├── guideline_chunker.py # Semantic chunking of guidelines
│       ├── retriever.py         # FAISS vector search
│       ├── reasoner.py          # Ollama LLM reasoning
│       ├── citation_checker.py  # Self-citation verification
│       ├── report_builder.py    # AuditReport assembly
│       └── statement_store.py   # Statement persistence
├── frontend/
│   └── app.py                   # Streamlit redliner UI
├── data/
│   ├── raw/                     # Source PDFs
│   └── processed/               # FAISS index + SQLite DB
├── models/
│   └── embedding_index/         # Pre-built guideline embeddings
├── tests/
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload-protocol` | Upload and parse a protocol/CER PDF |
| POST | `/upload-guideline` | Upload and index a new guideline PDF |
| POST | `/audit` | Run full compliance audit on uploaded protocol |
| GET | `/audit/{audit_id}` | Retrieve a previously generated audit report |
| GET | `/health` | Liveness check |
| GET | `/status` | Readiness check (index status, model info) |

---

## Built At

**Ethosh IGNITE 2026 Hackathon**

## Author
Vedant Vinod Sankpal

B.Tech Computer Science and Engineering

Nutan College of Engineering and Research

GitHub: https://github.com/vedant2004x

Sushant Dattatray Garde

B.Tech Computer Science and Engineering

Nutan College of Engineering and Research

GitHub: https://github.com/sushantgarde

## License

MIT
