import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache registry to keep the model in memory
_loaded_model = None
_loaded_tokenizer = None
_loaded_model_id = None

def load_model(
    model_name_or_path: str,
    lora_adapter_path: Optional[str] = None,
    use_4bit: bool = False, # Default to False for your CPU work laptop
) -> tuple:
    global _loaded_model, _loaded_tokenizer, _loaded_model_id

    model_key = f"{model_name_or_path}::{lora_adapter_path}"
    if _loaded_model_id == model_key:
        logger.info("Model already loaded — returning cached instance.")
        return _loaded_model, _loaded_tokenizer

    logger.info(f"Loading tokenizer: {model_name_or_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    logger.info(f"Loading base model onto CPU memory: {model_name_or_path}")
    # We remove quantization configs entirely here since use_4bit=False on this laptop
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        device_map="cpu", # Explicitly force CPU allocation to prevent accelerate crashes
        low_cpu_mem_usage=True,
        trust_remote_code=True,
        torch_dtype=torch.float32 # Standard precision for CPU execution
    )

    model.eval()

    _loaded_model = model
    _loaded_tokenizer = tokenizer
    _loaded_model_id = model_key

    logger.info("🎉 Model loaded on CPU and ready!")
    return model, tokenizer

def get_loaded_model():
    return _loaded_model, _loaded_tokenizer

def run_inference(prompt: str, max_new_tokens: int = 30) -> dict:
    """Runs a single inference pass on CPU and returns text + confidence metrics."""
    model, tokenizer = get_loaded_model()
    if model is None:
        raise RuntimeError("No model is loaded. Call load_model first.")

    # Convert characters to numerical tokens on CPU
    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False, # Greedy search for deterministic testing
            return_dict_in_generate=True,
            output_scores=True,
        )

    generated_ids = outputs.sequences[0][inputs["input_ids"].shape[-1]:]
    generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    # Collect per-token log probabilities for XAI metrics
    log_probs = []
    print(" Processing text generation layers...")
    for i,score in enumerate(outputs.scores):
        print(f"   -> Processing matrix calculations for token slot #{i+1}...")
        probs = torch.softmax(score, dim=-1)
        top_prob = probs.max(dim=-1).values.item()
        log_probs.append(top_prob)

    return {
        "prompt": prompt,
        "response": generated_text,
        "token_log_probs": log_probs,
        "avg_confidence": sum(log_probs) / len(log_probs) if log_probs else 0.0,
    }