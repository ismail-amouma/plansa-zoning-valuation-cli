from __future__ import annotations
from typing import Dict, Any
from settings import api_key, api_version, azure_endpoint

GRAPH_CONFIG: Dict[str, Any] = {
    "llm": {
        "model": "azure_openai/gpt-4o-mini",
        "api_key": api_key,
        "api_version": api_version,
        "azure_endpoint": azure_endpoint,
        "temperature": 0,
    },
    "verbose": True,
    "headless": False,
}