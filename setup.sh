#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Setting up Automated Tender Response System..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required but was not found."
    exit 1
fi

required_version="3.11"
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Python 3.11+ required. Found: $python_version"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt not found in $SCRIPT_DIR"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    if ! python3 -m venv venv; then
        echo "Failed to create virtual environment."
        echo "On Ubuntu/WSL, install it with: sudo apt-get install -y python3-venv"
        exit 1
    fi
else
    echo "Using existing virtual environment..."
fi

# shellcheck disable=SC1091
source venv/bin/activate

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

install_system_packages() {
    local packages=("$@")
    local installer=()

    if command -v sudo >/dev/null 2>&1; then
        installer=(sudo)
    elif [ "$(id -u)" -eq 0 ]; then
        installer=()
    else
        echo "Skipping system package install because sudo is unavailable."
        echo "Please install manually: ${packages[*]}"
        return 0
    fi

    "${installer[@]}" apt-get update
    "${installer[@]}" apt-get install -y "${packages[@]}"
}

# Install OCR/PDF dependencies
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get >/dev/null 2>&1; then
        echo "Installing Linux system packages..."
        install_system_packages tesseract-ocr tesseract-ocr-eng poppler-utils
    else
        echo "apt-get not found. Install these packages manually: tesseract-ocr tesseract-ocr-eng poppler-utils"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing MacOS system packages..."
    if command -v brew >/dev/null 2>&1; then
        brew install tesseract poppler
    else
        echo "Homebrew not found. Install Tesseract and Poppler manually."
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "Windows detected. Please install Tesseract manually from:"
    echo "https://github.com/UB-Mannheim/tesseract/wiki"
    echo "Also install Poppler and add both tools to PATH."
fi

mkdir -p workspace/uploads workspace/outputs workspace/history workspace/merged
mkdir -p static templates

echo "Pulling Ollama models..."
if command -v ollama >/dev/null 2>&1; then
    ollama pull llama3.2
    ollama pull mistral
    ollama pull phi3:medium
    echo "Models pulled successfully"
else
    echo "Ollama not found. Please install from https://ollama.ai"
    echo "Then run: ollama pull llama3.2"
    echo "Then run: ollama pull mistral"
    echo "Then run: ollama pull phi3:medium"
fi

echo
echo "Setup complete."
echo
echo "To start the application:"
echo "1. bash start.sh"
echo
echo "Then open http://localhost:8000 in your browser"
