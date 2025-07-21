from __future__ import annotations
from dotenv import load_dotenv
import os


load_dotenv()


LLM_PROVIDER=os.getenv("LLM_PROVIDER", None)
if LLM_PROVIDER=="openai":
    api_key = os.getenv("OPENAI_API_KEY", None)
    LLM_CONFIG={
        "model": "openai/gpt-4o-mini",
        "api_key": api_key,
        "temperature": 0,
    }
elif LLM_PROVIDER=="azure":
    api_key = os.getenv("AZURE_API_KEY", None)
    api_version = os.getenv("AZURE_API_VERSION",None )
    azure_endpoint = os.getenv("AZURE_ENDPOINT",None)
    LLM_CONFIG={
        "model": "azure_openai/gpt-4o-mini",
        "api_key": api_key,
        "api_version": api_version,
        "azure_endpoint": azure_endpoint,
        "temperature": 0,
    }