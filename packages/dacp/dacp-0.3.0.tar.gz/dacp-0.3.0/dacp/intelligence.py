"""
DACP Intelligence Module - Generic LLM provider interface.
"""

import os
import logging
from typing import Dict, Any, Optional

log = logging.getLogger(__name__)


class IntelligenceError(Exception):
    """Base exception for intelligence provider errors."""
    pass


class UnsupportedProviderError(IntelligenceError):
    """Raised when an unsupported intelligence provider is requested."""
    pass


class ConfigurationError(IntelligenceError):
    """Raised when intelligence configuration is invalid."""
    pass


def invoke_intelligence(prompt: str, config: Dict[str, Any]) -> str:
    """
    Invoke an intelligence provider (LLM) with the given prompt and configuration.
    
    Args:
        prompt: The input prompt to send to the intelligence provider
        config: Configuration dictionary containing provider details
        
    Returns:
        Response string from the intelligence provider
        
    Raises:
        UnsupportedProviderError: If the provider is not supported
        ConfigurationError: If the configuration is invalid
        IntelligenceError: For other provider-specific errors
    """
    engine = config.get("engine")
    if not engine:
        raise ConfigurationError("Missing 'engine' in intelligence configuration")
    
    engine = engine.lower()
    
    if engine == "openai":
        return _invoke_openai(prompt, config)
    elif engine == "anthropic":
        return _invoke_anthropic(prompt, config)
    elif engine == "azure":
        return _invoke_azure_openai(prompt, config)
    elif engine == "local":
        return _invoke_local(prompt, config)
    else:
        raise UnsupportedProviderError(f"Unsupported intelligence engine: {engine}")


def _invoke_openai(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke OpenAI provider."""
    try:
        import openai
    except ImportError:
        raise IntelligenceError("OpenAI package not installed. Run: pip install openai")
    
    model = config.get("model", "gpt-4")
    api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
    base_url = config.get("endpoint", "https://api.openai.com/v1")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 150)
    
    if not api_key:
        raise ConfigurationError("OpenAI API key not found in config or OPENAI_API_KEY environment variable")
    
    try:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise IntelligenceError("OpenAI returned empty response")
        return content
        
    except Exception as e:
        log.error(f"OpenAI API error: {e}")
        raise IntelligenceError(f"OpenAI API error: {e}")


def _invoke_anthropic(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke Anthropic (Claude) provider."""
    try:
        import anthropic
    except ImportError:
        raise IntelligenceError("Anthropic package not installed. Run: pip install anthropic")
    
    model = config.get("model", "claude-3-haiku-20240307")
    api_key = config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
    base_url = config.get("endpoint", "https://api.anthropic.com")
    max_tokens = config.get("max_tokens", 150)
    temperature = config.get("temperature", 0.7)
    
    if not api_key:
        raise ConfigurationError("Anthropic API key not found in config or ANTHROPIC_API_KEY environment variable")
    
    try:
        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        
        if not response.content or len(response.content) == 0:
            raise IntelligenceError("Anthropic returned empty response")
        
        # Anthropic returns a list of content blocks
        return response.content[0].text
        
    except Exception as e:
        log.error(f"Anthropic API error: {e}")
        raise IntelligenceError(f"Anthropic API error: {e}")


def _invoke_azure_openai(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke Azure OpenAI provider."""
    try:
        import openai
    except ImportError:
        raise IntelligenceError("OpenAI package not installed. Run: pip install openai")
    
    model = config.get("model", "gpt-4")
    api_key = config.get("api_key") or os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = config.get("endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = config.get("api_version", "2024-02-01")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 150)
    
    if not api_key:
        raise ConfigurationError("Azure OpenAI API key not found in config or AZURE_OPENAI_API_KEY environment variable")
    
    if not endpoint:
        raise ConfigurationError("Azure OpenAI endpoint not found in config or AZURE_OPENAI_ENDPOINT environment variable")
    
    try:
        client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise IntelligenceError("Azure OpenAI returned empty response")
        return content
        
    except Exception as e:
        log.error(f"Azure OpenAI API error: {e}")
        raise IntelligenceError(f"Azure OpenAI API error: {e}")


def _invoke_local(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke local LLM provider (e.g., Ollama, local API)."""
    import requests
    
    endpoint = config.get("endpoint", "http://localhost:11434/api/generate")
    model = config.get("model", "llama2")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 150)
    
    try:
        # Format for Ollama API
        if "ollama" in endpoint or ":11434" in endpoint:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
        else:
            # Generic local API format
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Handle different response formats
        if "response" in result:
            return result["response"]  # Ollama format
        elif "text" in result:
            return result["text"]      # Generic format
        elif "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0].get("text", "")  # OpenAI-compatible format
        else:
            raise IntelligenceError(f"Unexpected response format from local provider: {result}")
            
    except requests.RequestException as e:
        log.error(f"Local provider request error: {e}")
        raise IntelligenceError(f"Local provider request error: {e}")
    except Exception as e:
        log.error(f"Local provider error: {e}")
        raise IntelligenceError(f"Local provider error: {e}")


def get_supported_engines() -> list:
    """Get list of supported intelligence engines."""
    return ["openai", "anthropic", "azure", "local"]


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate intelligence configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    if not isinstance(config, dict):
        raise ConfigurationError("Configuration must be a dictionary")
    
    engine = config.get("engine")
    if not engine:
        raise ConfigurationError("Missing 'engine' in configuration")
    
    if engine.lower() not in get_supported_engines():
        raise ConfigurationError(f"Unsupported engine: {engine}. Supported engines: {get_supported_engines()}")
    
    # Engine-specific validation
    engine = engine.lower()
    
    if engine in ["openai", "azure"]:
        if not config.get("api_key") and not os.getenv("OPENAI_API_KEY") and not os.getenv("AZURE_OPENAI_API_KEY"):
            raise ConfigurationError(f"API key required for {engine} engine")
    
    elif engine == "anthropic":
        if not config.get("api_key") and not os.getenv("ANTHROPIC_API_KEY"):
            raise ConfigurationError("API key required for Anthropic engine")
    
    elif engine == "local":
        if not config.get("endpoint"):
            config["endpoint"] = "http://localhost:11434/api/generate"  # Default to Ollama
    
    return True 