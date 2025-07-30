from __future__ import annotations

from pathlib import Path
from typing import Tuple

from torch import nn

import torch
from safetensors.torch import load_file
from transformers import AutoModelForCausalLM, AutoTokenizer

from .low_rank_layer import LowRankRedistributor


def _load_similarity(path: str, device: torch.device) -> torch.Tensor:
    p = Path(path)
    if p.is_dir():
        p = p / "W.safetensors"
    if p.suffix == ".safetensors":
        state = load_file(str(p), "cpu" if device.type == "cpu" else device.index)
    else:
        state = torch.load(str(p), device)
    tensor = state["W"] if "W" in state else state["similarity"]
    if device is not None and tensor.device != device:
        tensor = tensor.to(device)
    return tensor


def load_wrapped_model(
    model_name_or_path: str,
    similarity: str,
    alpha: float = 0.0,
    device: torch.device = torch.device("cpu"),
) -> Tuple[AutoModelForCausalLM, AutoTokenizer, nn.Module]:
    """Load a model and attach the similarity redistribution layer.

    Parameters
    ----------
    model_name_or_path:
        Hugging Face model identifier or local path understood by
        ``AutoModelForCausalLM.from_pretrained``.
    similarity:
        Directory containing ``W.safetensors`` or a file with the sparse
        similarity matrix under the key ``"W"`` or ``"similarity"``.
    alpha:
        Strength of demotion for the original logits. ``0`` disables demotion.
    """

    model = AutoModelForCausalLM.from_pretrained(model_name_or_path)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    W = _load_similarity(similarity, device)
    layer: nn.Module = LowRankRedistributor(W, alpha=alpha)
    return model, tokenizer, layer
