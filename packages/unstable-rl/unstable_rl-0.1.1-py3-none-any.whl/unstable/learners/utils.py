import torch, pathlib
from typing import Dict, Any, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft.tuners.lora import LoraLayer
from peft import LoraConfig, get_peft_model, set_peft_model_state_dict
try:                from torch.utils.checkpoint import CheckpointImpl
except ImportError: from torch.distributed.algorithms._checkpoint.checkpoint_wrapper import CheckpointImpl
from torch.distributed.algorithms._checkpoint.checkpoint_wrapper import checkpoint_wrapper, apply_activation_checkpointing

def _load_lora_state(peft_model, ckpt_dir: str | pathlib.Path):
    ckpt_dir = pathlib.Path(ckpt_dir)
    candidates = [ckpt_dir / "adapter_model.safetensors", ckpt_dir / "adapter_model.bin", ckpt_dir / "pytorch_model.bin",]
    for path in candidates:
        if path.exists():
            print(f"[loader] found LoRA adapter → {path.name}")
            lora_sd = safe_load(str(path)) if path.suffix == ".safetensors" else torch.load(path, map_location="cpu")
            set_peft_model_state_dict(peft_model, lora_sd, adapter_name="default")
            return
    raise FileNotFoundError(f"No adapter_model.* found in {ckpt_dir}")

def build_peft_model(base_name: str, device: torch.device, lora_cfg: Dict[str, Any] | None, initial_lora_path: Optional[str], freeze_base: bool = True):
    print(f"[Learner] Loading base model: {base_name} ...")
    try:
        with torch.device(device):
            base = AutoModelForCausalLM.from_pretrained(base_name, torch_dtype=torch.bfloat16, trust_remote_code=True, attn_implementation="flash_attention_2")
        base.config._attn_implementation = "flash_attention_2" # try forcing it # TODO not really working I think
    except Exception as exc:
        print(f"Flash attention not available.")
        with torch.device(device):
            base = AutoModelForCausalLM.from_pretrained(base_name, torch_dtype=torch.bfloat16, trust_remote_code=True)

    
    if freeze_base:
        for p in base.parameters(): p.requires_grad_(False)
    lcfg = LoraConfig(
        r=lora_cfg.get("lora_rank", 32), lora_alpha=lora_cfg.get("lora_alpha", 32), lora_dropout=lora_cfg.get("lora_dropout", 0.05),
        bias="none", task_type="CAUSAL_LM", target_modules=lora_cfg.get("target_modules", ["q_proj", "k_proj", "v_proj", "o_proj"]),
    )
    model = get_peft_model(base, lcfg).to(device)

    if initial_lora_path:
        print(f"[Learner] Loading initial LoRA weights from {initial_lora_path}")
        _load_lora_state(model, initial_lora_path)

    tok = AutoTokenizer.from_pretrained(base_name, trust_remote_code=True)
    tok.pad_token = tok.eos_token  # safe default
    return model, tok

def _json_safe(obj):
    if isinstance(obj, set): return list(obj) # turn sets into lists
    raise TypeError # let json handle the rest
    
def enable_full_activation_ckpt(model):
    def checkpoint_everything(mod):
        if isinstance(mod, LoraLayer): return False
        for _, child in mod.named_modules():
            if isinstance(child, LoraLayer):
                return False
        return True
    apply_activation_checkpointing(model, checkpoint_wrapper_fn=lambda m: checkpoint_wrapper(m, checkpoint_impl=CheckpointImpl.NO_REENTRANT), check_fn=checkpoint_everything)  # “always recompute”