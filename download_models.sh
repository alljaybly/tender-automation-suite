#!/bin/bash
# Simple downloader using wget (no Python needed)

MODEL_DIR="$HOME/models"
mkdir -p "$MODEL_DIR"
cd "$MODEL_DIR"

echo "📥 Downloading models to $MODEL_DIR..."

# Model 1: Gemma 2 2B (Smallest, works on 6GB)
echo "⬇️  Downloading Gemma 2 2B (~1.6GB)..."
wget --progress=bar:force -c \
    "https://huggingface.co/unsloth/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it.Q4_K_M.gguf" \
    -O "gemma-2-2b-it.Q4_K_M.gguf"

# Model 2: Llama 3.2 3B (Better quality, ~2GB)
echo "⬇️  Downloading Llama 3.2 3B (~2GB)..."
wget --progress=bar:force -c \
    "https://huggingface.co/unsloth/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct.Q4_K_M.gguf" \
    -O "Llama-3.2-3B-Instruct.Q4_K_M.gguf"

# Model 3: Qwen 2.5 3B (Alternative, good for analysis)
echo "⬇️  Downloading Qwen 2.5 3B (~1.9GB)..."
wget --progress=bar:force -c \
    "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct.Q4_K_M.gguf" \
    -O "qwen2.5-3b-instruct.Q4_K_M.gguf"

echo ""
echo "✅ Downloads complete!"
ls -lh "$MODEL_DIR"/*.gguf
