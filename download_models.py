#!/usr/bin/env python3
"""Download GGUF models using huggingface_hub - WORKING VERSION."""
import os
from pathlib import Path

# Create models directory
models_dir = Path("/mnt/c/Users/allan/OneDrive/Documents/tender_system/models")
models_dir.mkdir(parents=True, exist_ok=True)
os.chdir(models_dir)

print("="*60)
print("📥 Downloading GGUF Models")
print("="*60)

# Model 1: Llama 3.2 3B (for reasoning tasks)
print("\n🦙 Downloading Llama 3.2 3B (Q4_K_M)...")
try:
    from huggingface_hub import hf_hub_download
    import requests
    
    # Try direct download from Hugging Face
    url = "https://huggingface.co/unsloth/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct.Q4_K_M.gguf"
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        with open("Llama-3.2-3B-Instruct.Q4_K_M.gguf", 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    percent = (downloaded / total_size) * 100
                    print(f"   Progress: {percent:.1f}%", end='\r')
        print(f"\n   ✅ Downloaded Llama-3.2-3B-Instruct.Q4_K_M.gguf")
    else:
        print(f"   ❌ Direct download failed: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Model 2: Gemma 2 2B (for quick tasks)
print("\n🦙 Downloading Gemma 2 2B (Q4_K_M)...")
try:
    url = "https://huggingface.co/unsloth/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it.Q4_K_M.gguf"
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        with open("gemma-2-2b-it.Q4_K_M.gguf", 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    percent = (downloaded / total_size) * 100
                    print(f"   Progress: {percent:.1f}%", end='\r')
        print(f"\n   ✅ Downloaded gemma-2-2b-it.Q4_K_M.gguf")
    else:
        print(f"   ❌ Direct download failed: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Model 3: Phi-3 Mini (already have or download)
print("\n🔍 Checking for Phi-3 Mini...")
phi_path = Path("/mnt/c/Users/allan/OneDrive/Documents/Myclaw/myclaw/models/phi-3-mini-4k-instruct-q4.gguf")
if phi_path.exists():
    import shutil
    shutil.copy(phi_path, models_dir / "phi-3-mini-4k-instruct-q4.gguf")
    print(f"   ✅ Copied Phi-3 Mini from existing location")
else:
    print(f"   ⚠️ Phi-3 Mini not found - will use Llama as fallback")

print("\n" + "="*60)
print("✅ Download complete!")
print("="*60)
print(f"📁 Models saved to: {models_dir}")
