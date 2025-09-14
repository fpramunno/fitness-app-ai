#!/usr/bin/env python3
"""
Quick model switcher for testing different models
"""

import json
import sys

def switch_model(model_name):
    """Switch the active model in model_config.json"""
    
    # Load current config
    with open('model_config.json', 'r') as f:
        config = json.load(f)
    
    # Available models
    available_models = {
        'gpt2': {
            'base_model': 'gpt2',
            'max_new_tokens': 100,
            'temperature': 0.3
        },
        'gpt2-medium': {
            'base_model': 'gpt2-medium',
            'max_new_tokens': 150,
            'temperature': 0.5
        },
        'gpt2-large': {
            'base_model': 'gpt2-large',
            'max_new_tokens': 200,
            'temperature': 0.6
        },
        'gpt2-xl': {
            'base_model': 'gpt2-xl',
            'max_new_tokens': 250,
            'temperature': 0.6
        },
        'llama2-7b': {
            'base_model': 'meta-llama/Llama-2-7b-hf',
            'max_new_tokens': 600,
            'temperature': 0.7
        },
        'mistral-7b': {
            'base_model': 'mistralai/Mistral-7B-v0.1',
            'max_new_tokens': 300,
            'temperature': 0.7
        },
        'phi2': {
            'base_model': 'microsoft/phi-2',
            'max_new_tokens': 250,
            'temperature': 0.6
        },
        'gemma-2b': {
            'base_model': 'google/gemma-2b',
            'max_new_tokens': 250,
            'temperature': 0.6
        },
        'qwen-1.8b': {
            'base_model': 'Qwen/Qwen1.5-1.8B',
            'max_new_tokens': 250,
            'temperature': 0.6
        },
        'dialogpt': {
            'base_model': 'microsoft/DialoGPT-small',
            'max_new_tokens': 150,
            'temperature': 0.6
        },
        'mobilellm': {
            'base_model': 'facebook/MobileLLM-R1-950M',
            'max_new_tokens': 200,
            'temperature': 0.7
        },
        'exaone-2.4b': {
            'base_model': 'LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct',
            'max_new_tokens': 300,
            'temperature': 0.6
        }
    }
    
    if model_name not in available_models:
        print(f"❌ Model '{model_name}' not available.")
        print(f"Available models: {', '.join(available_models.keys())}")
        return False
    
    # Update config
    model_config = available_models[model_name]
    config['base_model'] = model_config['base_model']
    config['generation_config']['max_new_tokens'] = model_config['max_new_tokens']
    config['generation_config']['temperature'] = model_config['temperature']
    
    # Save updated config
    with open('model_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Switched to {model_config['base_model']}")
    print(f"   Max tokens: {model_config['max_new_tokens']}")
    print(f"   Temperature: {model_config['temperature']}")
    print("\n⚠️  Restart model_server.py to apply changes!")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python switch_model.py <model_name>")
        print("Available models:")
        print("  🚀 RECOMMENDED (Newer & Better):")
        print("    exaone-2.4b - LG EXAONE 3.5 2.4B (state-of-the-art, efficient)")
        print("    mistral-7b  - Mistral 7B (excellent quality, 7B params)")
        print("    phi2        - Microsoft Phi-2 (2.7B, very capable)")
        print("    qwen-1.8b   - Qwen 1.5 1.8B (good balance)")
        print("    gemma-2b    - Google Gemma 2B (instruction-tuned)")
        print("")
        print("  📈 GPT-2 Series (Older but reliable):")
        print("    gpt2-xl     - GPT-2 XL (1.5B, best GPT-2)")
        print("    gpt2-large  - GPT-2 Large (774M)")
        print("    gpt2-medium - GPT-2 Medium (355M)")
        print("    gpt2        - GPT-2 Small (124M, fast)")
        print("")
        print("  🔒 Requires Approval:")
        print("    llama2-7b   - Meta Llama 2 7B (needs HuggingFace approval)")
        print("    mobilellm   - Facebook MobileLLM (needs approval)")
        print("")
        print("💡 Recommendations:")
        print("   • Best overall: exaone-2.4b (state-of-the-art efficiency)")
        print("   • Best quality: mistral-7b or phi2")
        print("   • Good balance: qwen-1.8b or gemma-2b")
        print("   • Fastest: gpt2-medium")
        print("\nExample: python switch_model.py mistral-7b")
        sys.exit(1)
    
    model_name = sys.argv[1].lower()
    switch_model(model_name)