"""
Legacy LLM module - Provides backward compatibility for call_llm function.
Uses the new intelligence module under the hood.
"""

import os
from .intelligence import invoke_intelligence


def call_llm(prompt: str, model: str = "gpt-4") -> str:
    """
    Legacy function for calling LLMs. 
    Maintained for backward compatibility.
    
    Args:
        prompt: The input prompt
        model: The model to use (defaults to gpt-4)
        
    Returns:
        Response from the LLM
    """
    # Create OpenAI config for backward compatibility
    config = {
        "engine": "openai",
        "model": model,
        "api_key": os.getenv("OPENAI_API_KEY"),
        "endpoint": "https://api.openai.com/v1",
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    return invoke_intelligence(prompt, config)
