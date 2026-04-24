# Quick Start

This is the shortest path to get the project running on Ubuntu or WSL.

## Prerequisites

- Ubuntu or WSL
- Python 3.11+
- internet access for package installation

## Start In 4 Steps

### 1. Open the project

```bash
cd /mnt/c/Users/allan/OneDrive/Documents/tender_system
```

### 2. Run setup

```bash
bash setup.sh
```

This will:

- create or reuse `venv`
- install Python dependencies
- install OCR tools on supported Ubuntu systems
- create required workspace folders

### 3. Set optional Groq key

If you want cloud pricing debate instead of fallback pricing:

```bash
export GROQ_API_KEY="your_api_key"
```

Or copy [.env.example](file:///c:/Users/allan/OneDrive/Documents/tender_system/.env.example) to `.env` and set `GROQ_API_KEY` there.

If you skip this step, the app still runs and uses local fallback pricing logic.

### 4. Start the app

```bash
bash start.sh
```

Then open:

- `http://localhost:8000`

## Manual Start

If you want to run the server manually:

```bash
source venv/bin/activate
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Common Fixes

### Missing virtual environment

```bash
bash setup.sh
```

### OCR not working

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
```

### Missing Python packages

```bash
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Key Locations

- `workspace/uploads`
- `workspace/outputs`
- `workspace/history`
- `workspace/merged`

## Full Documentation

See [README.md](file:///c:/Users/allan/OneDrive/Documents/tender_system/README.md) for full setup, API usage, troubleshooting, and architecture notes.
