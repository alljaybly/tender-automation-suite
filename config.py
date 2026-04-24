# config.py - Optimized for your 6GB RAM + available models

import os
from pathlib import Path

from env_loader import load_env_file

load_env_file(Path(__file__).resolve().parent / ".env")

# Model Configuration
MODELS = {
    # Local Model 1: Phi-3 Mini (2.3GB) - Best quality you have
    "cost_accountant": {
        "path": "models/phi-3-mini-Q4_K_M.gguf",
        "type": "local",
        "n_ctx": 2048,        # Lower = less RAM
        "n_threads": 4,       # Your 4 cores
    },
    
    # Local Model 2: Gemma 3 1B (800MB) - Fast, small
    "market_analyst": {
        "path": "models/gemma-3-1b-it-Q4_K_M.gguf", 
        "type": "local",
        "n_ctx": 2048,
        "n_threads": 4,
    },
    
    # Cloud Model 3: Groq (0 RAM usage) - Risk assessment needs big brain
    "risk_assessor": {
        "type": "cloud",
        "api_key": os.getenv("GROQ_API_KEY", ""),
        "model": "llama-3.3-70b-versatile",  # 70B params via API
        "base_url": "https://api.groq.com/openai/v1",
    }
}

# Memory Management
MAX_RAM_GB = 5.0  # Leave 1GB for OS
