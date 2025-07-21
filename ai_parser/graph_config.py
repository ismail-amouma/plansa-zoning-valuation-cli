from __future__ import annotations
from typing import Dict, Any
from settings import LLM_CONFIG

GRAPH_CONFIG: Dict[str, Any] = {
    "llm": LLM_CONFIG,
    "verbose": True,
    "headless": False,
}