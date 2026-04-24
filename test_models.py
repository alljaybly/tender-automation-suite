from llama_cpp import Llama
import os
import gc

def test_model(path, name):
    print(f"\n🔍 Testing {name}...")
    print(f"   Path: {path}")
    
    if not os.path.exists(path):
        print(f"   ❌ File not found!")
        return False
        
    try:
        # Try to load with minimal settings
        llm = Llama(
            model_path=path,
            n_ctx=512,  # Very small context for testing
            verbose=False,
            use_mmap=True,
        )
        
        # Test generation
        output = llm("Price this tender at R", max_tokens=10)
        result = output['choices'][0]['text']
        
        print(f"   ✅ Loaded successfully!")
        print(f"   📝 Sample output: {result[:50]}...")
        
        del llm
        gc.collect()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Test what you have
    test_model("models/phi-3-mini-Q4_K_M.gguf", "Phi-3 Mini")
    test_model("models/gemma-3-1b-it-Q4_K_M.gguf", "Gemma 3 1B")
