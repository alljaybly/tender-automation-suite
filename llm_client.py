# llm_client.py - Memory-optimized LLM client
import os
import json
import aiohttp
from typing import Optional, List, Dict
from dataclasses import dataclass

# Try to import llama_cpp, fallback to API if not available
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

@dataclass
class ModelInstance:
    name: str
    path: Optional[str] = None  # Local path to .gguf
    api_config: Optional[Dict] = None  # Cloud API config
    llama_instance: Optional[Llama] = None
    
class MemoryEfficientDebate:
    """Rotates models in/out of memory for low-RAM systems"""
    
    def __init__(self, max_ram_gb: float = 5.0):
        self.max_ram = max_ram_gb * 1024**3  # Convert to bytes
        self.models: Dict[str, ModelInstance] = {}
        self.active_model: Optional[str] = None
        
    async def load_model(self, model_key: str, gguf_path: str, n_ctx: int = 2048):
        """Load a quantized model with memory constraints"""
        if not LLAMA_CPP_AVAILABLE:
            raise RuntimeError("llama-cpp-python not installed")
            
        # Unload current model to free RAM
        if self.active_model and self.active_model in self.models:
            print(f"Unloading {self.active_model} to free RAM...")
            self.models[self.active_model].llama_instance = None
            import gc
            gc.collect()
        
        print(f"Loading {model_key} from {gguf_path}...")
        
        # Load with aggressive memory settings
        llm = Llama(
            model_path=gguf_path,
            n_ctx=n_ctx,              # Shorter context = less RAM
            n_threads=4,              # Your 4 cores
            n_batch=512,              # Smaller batches
            use_mmap=True,            # Memory mapping (crucial for 6GB)
            use_mlock=False,          # Don't lock pages
            verbose=False
        )
        
        self.models[model_key] = ModelInstance(
            name=model_key,
            path=gguf_path,
            llama_instance=llm
        )
        self.active_model = model_key
        
        return llm
    
    async def generate(self, model_key: str, prompt: str, max_tokens: int = 500) -> str:
        """Generate with automatic model swapping"""
        if model_key not in self.models or not self.models[model_key].llama_instance:
            # Model not loaded - need to load first
            if model_key == "cost_accountant":
                path = "~/models/phi-3-mini-4k-instruct-q4.gguf"
            elif model_key == "market_analyst":
                path = "~/models/llama-3.2-3b-instruct-q4.gguf"
            else:  # risk_assessor
                path = "~/models/gemma-2-2b-it-q4.gguf"
                
            await self.load_model(model_key, os.path.expanduser(path))
        
        llm = self.models[model_key].llama_instance
        
        output = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            stop=["</s>", "User:", "Assistant:"],
            echo=False
        )
        
        return output['choices'][0]['text']
    
    async def cloud_generate(self, api_config: Dict, prompt: str) -> str:
        """Fallback to API for third model if RAM full"""
        headers = {
            "Authorization": f"Bearer {api_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": api_config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_config['base_url']}/chat/completions",
                headers=headers,
                json=payload
            ) as resp:
                result = await resp.json()
                return result['choices'][0]['message']['content']
