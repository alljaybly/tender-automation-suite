# TenderFlow AI: SaaS Tender Workspace

AI-powered tender analysis and professional response generation platform for modern contractors.

## 🚀 SaaS Edition

TenderFlow has evolved from a simple script into a professional **Tender Workspace** designed for businesses to manage their entire bidding pipeline.

### Pricing Tiers

| Feature | **Free** | **Pro** ($49/mo) |
| :--- | :--- | :--- |
| **Usage** | 1 Tender / Day | Unlimited Tenders |
| **Analysis** | Basic Pricing | Advanced Scoring & Benchmarking |
| **Branding** | Standard Templates | Custom Logo & Company Branding |
| **AI Debate** | Standard | Priority Cloud Debate (Groq/Mistral) |
| **Storage** | Local History | Full Workspace Library |
| **Support** | Community | Priority Email Support |

### How to Upgrade
Currently in **Beta**. Use the "Upgrade" button in the dashboard to join the waitlist. 
*Developers: Use `X-API-Key: PRO-TRIAL-2026` to bypass limits during testing.*

## 🗺️ Roadmap

- [x] **Workspace Library** – Manage and search historical tenders.
- [x] **Branded Outputs** – Dynamic logo and company name injection.
- [x] **SaaS Tiers** – Usage limits and Pro feature gates.
- [ ] **Multi-User Teams** – Collaborate on tender drafts.
- [ ] **Stripe Integration** – Real-time subscription management.
- [ ] **Direct Submission** – API integration with government portals.

## Why This Tool Exists
...

Small contractors in South Africa lose tenders because:
- They underprice due to fear of missing requirements
- They miss compliance deadlines due to unclear documentation requirements
- They spend hours manually creating tender documents

This tool helps contractors:
- **Price accurately** by comparing against market rates and running a pricing debate
- **Stay compliant** with sector-specific document checklists
- **Win more** by understanding their competitive position before submission
- **Save time** by auto-generating Word and Excel tender documents

This project provides a web dashboard and API that can:

- upload tender documents
- extract text and key requirements from PDF, DOCX, DOC, TXT, RTF, and common image formats
- run OCR for scanned PDFs
- estimate staffing, duration, scope, and pricing inputs
- research reference rates from the web
- run a pricing debate flow using Groq models when configured
- fall back to local pricing logic when no valid Groq key is available
- generate Word and Excel tender output files

## Additional Docs

- [README_QUICKSTART.md](file:///c:/Users/allan/OneDrive/Documents/tender_system/README_QUICKSTART.md) for the fastest local setup path
- [DEPLOYMENT.md](file:///c:/Users/allan/OneDrive/Documents/tender_system/DEPLOYMENT.md) for Ubuntu server or VPS deployment
- [.env.example](file:///c:/Users/allan/OneDrive/Documents/tender_system/.env.example) for environment variable setup reference

## What This Project Does

The application is built with FastAPI and serves a browser dashboard at `http://localhost:8000`.

Typical workflow:

1. Upload one or more tender files.
2. The backend stores the files in `workspace/uploads`.
3. Text is extracted from PDFs, Word files, text files, or images.
4. The system estimates tender structure such as sector, duration, workers, and scope.
5. It looks up market and labour rate references.
6. It runs a pricing analysis/debate stage.
7. It generates final documents in Word and Excel format.
8. It stores run history in `workspace/history`.

## Demo Workflow

Get started instantly without uploading any files:

1. Click **🚀 Try Demo** on the main dashboard.
2. Select a tender type: **Cleaning**, **Security**, or **Construction**.
3. The system generates a sample tender and processes it automatically.
4. View results, pricing breakdown, win score, and compliance checklist.
5. Edit the draft content as needed.
6. Download the generated Word and Excel documents.

Demo data is stored temporarily in `workspace/uploads` and processed just like uploaded files.

## Current Capabilities

### Document Handling

- PDF text extraction with `pdfplumber`
- OCR fallback for scanned PDFs using `pytesseract` and `pdf2image`
- DOCX parsing with `python-docx`
- basic support for DOC, TXT, and RTF text extraction
- package merging for multiple uploaded text-like files

### Tender Analysis

- sector detection
- worker estimation
- duration extraction
- scope estimation
- location extraction
- requirements normalization for downstream pricing and document generation

### Pricing

- web search based rate gathering
- Groq-based debate flow when `GROQ_API_KEY` is set
- local fallback calculation when cloud pricing is unavailable

### Outputs

- `.docx` tender submission document
- `.xlsx` pricing workbook
- JSON history records

## Key Features

- **Editable Draft Mode** – Review and modify your tender's executive summary, scope description, and pricing notes before final download. Save drafts for later revision.
- **Tender Win Score** – Get an instant win probability assessment with risk level, identified issues, and improvement suggestions.
- **Smart Compliance Checklist** – Automatically generated document requirements based on tender sector (cleaning, security, construction, etc.).
- **Multi-Sector Support** – Handles cleaning, construction, electrical, security, plumbing, gardening, and general services tenders.
- **AI-Assisted Pricing Debate** – Uses Groq-powered debate council to validate pricing assumptions when API key is configured.
- **Document Generation** – Produces professional Word (.docx) and Excel (.xlsx) tender submissions.
- **Demo Mode** – Try the system instantly with pre-loaded sample tenders (cleaning, security, or construction).

## Supported Tender Types

The code currently contains sector logic for:

- cleaning
- construction
- electrical
- security
- plumbing
- gardening
- general services
- IT-related matches through keyword detection

## Tech Stack

- FastAPI
- Uvicorn
- Jinja2 templates
- WebSockets
- `pdfplumber`
- `pytesseract`
- `pdf2image`
- `python-docx`
- `openpyxl`
- `duckduckgo-search`
- `aiohttp`

## Project Structure

```text
tender_system/
|-- app.py
|-- setup.sh
|-- start.sh
|-- requirements.txt
|-- templates/
|   `-- index.html
|-- static/
|-- models/
|-- workspace/
|   |-- uploads/
|   |-- outputs/
|   |-- history/
|   `-- merged/
|-- pdf_processor.py
|-- web_search.py
|-- debate_council.py
|-- pricing_engine.py
`-- document_generator.py
```

## Requirements

### Required

- Python 3.11 or newer
- pip
- virtual environment support for Python

### Recommended for Ubuntu/WSL

- Tesseract OCR
- Poppler utilities

These are required for OCR and scanned PDF processing.

### Optional

- `GROQ_API_KEY` for cloud debate pricing
- Ollama if you want local model tooling available in your environment

Note: the current pricing debate implementation uses Groq when configured and falls back to local calculation when no valid key is present.

## Quick Start On Ubuntu Or WSL

### 1. Open the project

```bash
cd path/to/tender_system
```

### 2. Run setup

```bash
bash setup.sh
```

What `setup.sh` does:

- checks Python version
- creates or reuses `venv`
- installs Python dependencies
- installs OCR system packages on supported Linux systems
- creates required working directories
- attempts to pull Ollama models if `ollama` is installed

### 3. Start the server

```bash
bash start.sh
```

The app runs on:

- `http://localhost:8000`

### 4. Open the dashboard

In your browser, visit:

- `http://localhost:8000`

## Manual Start Commands

If you prefer not to use `start.sh`:

```bash
source venv/bin/activate
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Windows Notes

This repository is currently easiest to run inside Ubuntu/WSL.

If you run directly on Windows:

- create a Windows virtual environment yourself
- install Python packages from `requirements.txt`
- install Tesseract manually
- install Poppler manually if OCR or image-based PDF conversion is needed

## Environment Variables

### `GROQ_API_KEY`

Optional, but useful for the cloud pricing debate flow.

You can set it either:

- in your shell environment
- in a local `.env` file created from [.env.example](file:///c:/Users/allan/OneDrive/Documents/tender_system/.env.example)

The app auto-loads `.env` at startup, but existing shell environment variables take precedence.

Example:

```bash
export GROQ_API_KEY="gsk_your_key_here"
```

If this variable is missing or invalid:

- the app still runs
- the pricing debate falls back to local calculation logic

## How To Use The Application

### Upload Files

You can upload:

- `.pdf`
- `.docx`
- `.doc`
- `.txt`
- `.rtf`
- `.png`
- `.jpg`
- `.jpeg`

The backend accepts uploads through the dashboard or `POST /api/upload`.

### Process A Tender

After upload, the frontend uses the WebSocket endpoint:

- `/ws/process`

The processing pipeline sends progress updates such as:

- start
- pdf
- extracted
- search
- rates
- debate
- debate_complete
- pricing
- generating
- complete
- error

### Download Outputs

Generated files can be downloaded from:

- `/api/download/word/{filename}`
- `/api/download/excel/{filename}`

## API Overview

### Web Routes

- `GET /`  
  Serves the main dashboard.

### API Routes

- `GET /api/models`  
  Returns the configured cloud model list shown to the UI.

- `POST /api/upload`  
  Uploads one or more files and stores them in `workspace/uploads`.

- `GET /api/tender-comparison?tender_type=...&location=...`  
  Returns comparison data from stored history records.

- `POST /api/finalize-duration`  
  Recalculates duration-based pricing if the extracted contract period was wrong.

- `GET /api/history`  
  Lists historical run records.

- `GET /api/download/word/{filename}`  
  Downloads the generated Word document.

- `GET /api/download/excel/{filename}`  
  Downloads the generated Excel workbook.

- `GET /api/files/list`  
  Lists files in `workspace/outputs`.

- `POST /api/edit-draft`  
  Saves an edited version of the tender draft to `workspace/history`.

- `POST /api/regenerate`  
  Regenerates Word and Excel documents using modified draft content.

- `GET /api/win-score?tender_type=...&price=...&duration_months=...&workers=...`  
  Returns a tender win probability assessment and risk analysis.

- `GET /api/compliance-checklist?tender_type=...`  
  Generates a sector-specific mandatory document checklist.

- `POST /api/demo?tender_type=...`  
  Generates a sample tender document for testing (cleaning, security, or construction).

### WebSocket Route

- `WS /ws/process`  
  Starts the main tender processing workflow and streams progress updates.

## Example API Usage

### Upload a file with `curl`

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "files=@/path/to/tender.pdf"
```

### List generated files

```bash
curl "http://localhost:8000/api/files/list"
```

### View processing history

```bash
curl "http://localhost:8000/api/history"
```

## Output Locations

The application writes data under `workspace/`:

- `workspace/uploads` for original uploads
- `workspace/merged` for merged text packages
- `workspace/outputs` for generated Word and Excel files
- `workspace/history` for JSON processing history

## Main Modules

### `app.py`

Main FastAPI application, route definitions, upload handling, WebSocket processing, and file download endpoints.

### `pdf_processor.py`

Extracts text and infers tender structure such as sector, duration, workers, and area.

### `web_search.py`

Looks up rough labour, equipment, and materials rates using web search.

### `debate_council.py`

Runs the cloud pricing debate when `GROQ_API_KEY` is available and falls back to local pricing calculations otherwise.

### `pricing_engine.py`

Builds the final pricing structure used for document generation.

### `document_generator.py`

Creates the Word and Excel output documents.

## Troubleshooting

### `python3: command not found`

Install Python 3.11+ first.

### `No module named ...`

Run:

```bash
bash setup.sh
```

Or manually:

```bash
source venv/bin/activate
python -m pip install -r requirements.txt
```

### OCR Does Not Work

Install required system packages on Ubuntu/WSL:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
```

### The App Starts But Pricing Uses Fallback Logic

That usually means `GROQ_API_KEY` is missing or invalid.

Set it before launching the app:

```bash
export GROQ_API_KEY="gsk_your_key_here"
bash start.sh
```

### `start.sh` Says Virtual Environment Is Missing

Run:

```bash
bash setup.sh
```

### WSL Path Problems

Start from the project directory inside WSL:

```bash
cd path/to/tender_system
```

Then run:

```bash
bash setup.sh
bash start.sh
```

## Development Notes

- The app now resolves project directories relative to `app.py`, so it is less sensitive to the shell's current working directory.
- `start.sh` runs from its own script directory, so it is portable across Ubuntu/WSL locations.
- The repository contains model files and Ollama helper scripts, but the active pricing debate code currently depends on Groq when cloud mode is enabled.

## Limitations

- pricing and extraction quality depend heavily on source document quality
- OCR accuracy depends on scan quality and correct system package installation
- web-searched pricing references are heuristic and should be manually validated
- some sectors use estimated defaults when the source tender is incomplete
- the current implementation is best treated as an assisted drafting tool, not a final compliance authority

## Suggested Next Steps

- add a `.env.example` file for `GROQ_API_KEY`
- document the frontend processing flow with screenshots
- add automated API tests for upload and generation routes
- add a deployment guide for Linux server hosting
