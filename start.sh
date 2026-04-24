#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found at $SCRIPT_DIR/venv"
    echo "Run ./setup.sh first."
    exit 1
fi

source venv/bin/activate
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
