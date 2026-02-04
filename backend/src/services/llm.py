from __future__ import annotations

from functools import lru_cache
import logging
from typing import Optional

from langchain_community.llms import HuggingFacePipeline

from ..core.config import settings

logger = logging.getLogger("llm")


@lru_cache(maxsize=1)
def get_llm() -> Optional[HuggingFacePipeline]:
    if settings.llm_backend.lower() == "none":
        logger.warning("LLM backend disabled; using extractive fallback.")
        return None
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        dtype = getattr(torch, settings.llm_torch_dtype, torch.float32)
        device_setting = settings.llm_device.lower()
        if device_setting in ("auto", ""):
            device_setting = "cuda" if torch.cuda.is_available() else "cpu"
        device_str = "cpu"
        device_index = -1
        if device_setting.startswith("cuda"):
            if torch.cuda.is_available():
                if device_setting == "cuda":
                    device_str = "cuda:0"
                    device_index = 0
                else:
                    try:
                        device_index = int(device_setting.split(":")[1])
                        device_str = device_setting
                    except (IndexError, ValueError):
                        device_str = "cuda:0"
                        device_index = 0
            else:
                logger.warning("CUDA requested but not available; using CPU.")
        tokenizer = AutoTokenizer.from_pretrained(
            settings.llm_model_name, local_files_only=settings.llm_local_files_only
        )
        model = AutoModelForCausalLM.from_pretrained(
            settings.llm_model_name,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
            local_files_only=settings.llm_local_files_only,
        )
        if device_index >= 0:
            model = model.to(device_str)
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=settings.llm_max_tokens,
            do_sample=False,
            temperature=0.0,
            device=device_index,
        )
        return HuggingFacePipeline(pipeline=generator)
    except Exception as exc:  # pragma: no cover - environment dependent
        logger.exception("LLM load failed: %s", exc)
        return None
