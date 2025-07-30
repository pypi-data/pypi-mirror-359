"""
DACP Intelligence Module - Generic LLM provider interface.
"""

import os
import logging
from typing import Dict, Any, Optional

# Set up logger for this module
logger = logging.getLogger("dacp.intelligence")


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
        logger.error("❌ Missing 'engine' in intelligence configuration")
        raise ConfigurationError("Missing 'engine' in intelligence configuration")
    
    engine = engine.lower()
    model = config.get("model", "default")
    
    logger.info(f"🧠 Invoking intelligence: engine='{engine}', model='{model}'")
    logger.debug(f"📋 Prompt length: {len(prompt)} characters")
    logger.debug(f"⚙️  Full config: {_sanitize_config_for_logging(config)}")
    
    import time
    start_time = time.time()
    
    try:
        if engine == "openai":
            result = _invoke_openai(prompt, config)
        elif engine == "anthropic":
            result = _invoke_anthropic(prompt, config)
        elif engine == "azure":
            result = _invoke_azure_openai(prompt, config)
        elif engine == "local":
            result = _invoke_local(prompt, config)
        else:
            logger.error(f"❌ Unsupported intelligence engine: {engine}")
            raise UnsupportedProviderError(f"Unsupported intelligence engine: {engine}")
        
        execution_time = time.time() - start_time
        logger.info(f"✅ Intelligence response received in {execution_time:.3f}s (length: {len(result)} chars)")
        logger.debug(f"📤 Response preview: {result[:100]}{'...' if len(result) > 100 else ''}")
        
        return result
        
    except (IntelligenceError, UnsupportedProviderError, ConfigurationError):
        # Re-raise our own exceptions without modification
        execution_time = time.time() - start_time
        logger.error(f"❌ Intelligence call failed after {execution_time:.3f}s")
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Unexpected intelligence error after {execution_time:.3f}s: {type(e).__name__}: {e}")
        raise IntelligenceError(f"Unexpected error: {e}")


def _invoke_openai(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke OpenAI provider."""
    logger.debug("🔵 Initializing OpenAI provider")
    
    try:
        import openai
        logger.debug("✅ OpenAI package imported successfully")
    except ImportError:
        logger.error("❌ OpenAI package not installed")
        raise IntelligenceError("OpenAI package not installed. Run: pip install openai")
    
    model = config.get("model", "gpt-4")
    api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
    base_url = config.get("endpoint", "https://api.openai.com/v1")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 150)
    
    logger.debug(f"🔧 OpenAI config: model={model}, base_url={base_url}, temp={temperature}, max_tokens={max_tokens}")
    
    if not api_key:
        logger.error("❌ OpenAI API key not found")
        raise ConfigurationError("OpenAI API key not found in config or OPENAI_API_KEY environment variable")
    
    try:
        logger.debug("🔗 Creating OpenAI client")
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        
        logger.debug("📡 Sending request to OpenAI API")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        if content is None:
            logger.error("❌ OpenAI returned empty response")
            raise IntelligenceError("OpenAI returned empty response")
        
        logger.debug(f"✅ OpenAI API call successful")
        return content
        
    except Exception as e:
        logger.error(f"❌ OpenAI API error: {type(e).__name__}: {e}")
        raise IntelligenceError(f"OpenAI API error: {e}")


def _invoke_anthropic(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke Anthropic (Claude) provider."""
    logger.debug("🟣 Initializing Anthropic provider")
    
    try:
        import anthropic
        logger.debug("✅ Anthropic package imported successfully")
    except ImportError:
        logger.error("❌ Anthropic package not installed")
        raise IntelligenceError("Anthropic package not installed. Run: pip install anthropic")
    
    model = config.get("model", "claude-3-haiku-20240307")
    api_key = config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
    base_url = config.get("endpoint", "https://api.anthropic.com")
    max_tokens = config.get("max_tokens", 150)
    temperature = config.get("temperature", 0.7)
    
    logger.debug(f"🔧 Anthropic config: model={model}, base_url={base_url}, temp={temperature}, max_tokens={max_tokens}")
    
    if not api_key:
        logger.error("❌ Anthropic API key not found")
        raise ConfigurationError("Anthropic API key not found in config or ANTHROPIC_API_KEY environment variable")
    
    try:
        logger.debug("🔗 Creating Anthropic client")
        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
        
        logger.debug("📡 Sending request to Anthropic API")
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        
        if not response.content or len(response.content) == 0:
            logger.error("❌ Anthropic returned empty response")
            raise IntelligenceError("Anthropic returned empty response")
        
        # Anthropic returns a list of content blocks
        result = response.content[0].text
        logger.debug(f"✅ Anthropic API call successful")
        return result
        
    except Exception as e:
        logger.error(f"❌ Anthropic API error: {type(e).__name__}: {e}")
        raise IntelligenceError(f"Anthropic API error: {e}")


def _invoke_azure_openai(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke Azure OpenAI provider."""
    logger.debug("🔷 Initializing Azure OpenAI provider")
    
    try:
        import openai
        logger.debug("✅ OpenAI package imported successfully")
    except ImportError:
        logger.error("❌ OpenAI package not installed")
        raise IntelligenceError("OpenAI package not installed. Run: pip install openai")
    
    model = config.get("model", "gpt-4")
    api_key = config.get("api_key") or os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = config.get("endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = config.get("api_version", "2024-02-01")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 150)
    
    logger.debug(f"🔧 Azure config: model={model}, endpoint={endpoint}, api_version={api_version}, temp={temperature}, max_tokens={max_tokens}")
    
    if not api_key:
        logger.error("❌ Azure OpenAI API key not found")
        raise ConfigurationError("Azure OpenAI API key not found in config or AZURE_OPENAI_API_KEY environment variable")
    
    if not endpoint:
        logger.error("❌ Azure OpenAI endpoint not found")
        raise ConfigurationError("Azure OpenAI endpoint not found in config or AZURE_OPENAI_ENDPOINT environment variable")
    
    try:
        logger.debug("🔗 Creating Azure OpenAI client")
        client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        
        logger.debug("📡 Sending request to Azure OpenAI API")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        if content is None:
            logger.error("❌ Azure OpenAI returned empty response")
            raise IntelligenceError("Azure OpenAI returned empty response")
        
        logger.debug(f"✅ Azure OpenAI API call successful")
        return content
        
    except Exception as e:
        logger.error(f"❌ Azure OpenAI API error: {type(e).__name__}: {e}")
        raise IntelligenceError(f"Azure OpenAI API error: {e}")


def _invoke_local(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke local LLM provider (e.g., Ollama, local API)."""
    import requests
    
    endpoint = config.get("endpoint", "http://localhost:11434/api/generate")
    model = config.get("model", "llama2")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 150)
    
    logger.debug(f"🟢 Initializing local provider")
    logger.debug(f"🔧 Local config: model={model}, endpoint={endpoint}, temp={temperature}, max_tokens={max_tokens}")
    
    try:
        # Format for Ollama API
        if "ollama" in endpoint or ":11434" in endpoint:
            logger.debug("📦 Using Ollama API format")
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
            logger.debug("📦 Using generic local API format")
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        
        logger.debug(f"📡 Sending request to local endpoint: {endpoint}")
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Handle different response formats
        if "response" in result:
            response_text = result["response"]  # Ollama format
            logger.debug("✅ Local API call successful (Ollama format)")
        elif "text" in result:
            response_text = result["text"]      # Generic format
            logger.debug("✅ Local API call successful (generic format)")
        elif "choices" in result and len(result["choices"]) > 0:
            response_text = result["choices"][0].get("text", "")  # OpenAI-compatible format
            logger.debug("✅ Local API call successful (OpenAI-compatible format)")
        else:
            logger.error(f"❌ Unexpected response format from local provider: {result}")
            raise IntelligenceError(f"Unexpected response format from local provider: {result}")
        
        return response_text
            
    except requests.RequestException as e:
        logger.error(f"❌ Local provider request error: {type(e).__name__}: {e}")
        raise IntelligenceError(f"Local provider request error: {e}")
    except Exception as e:
        logger.error(f"❌ Local provider error: {type(e).__name__}: {e}")
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
    logger.debug(f"🔍 Validating intelligence configuration")
    
    if not isinstance(config, dict):
        logger.error("❌ Configuration must be a dictionary")
        raise ConfigurationError("Configuration must be a dictionary")
    
    engine = config.get("engine")
    if not engine:
        logger.error("❌ Missing 'engine' in configuration")
        raise ConfigurationError("Missing 'engine' in configuration")
    
    if engine.lower() not in get_supported_engines():
        logger.error(f"❌ Unsupported engine: {engine}")
        raise ConfigurationError(f"Unsupported engine: {engine}. Supported engines: {get_supported_engines()}")
    
    # Engine-specific validation
    engine = engine.lower()
    logger.debug(f"🔧 Validating {engine} specific configuration")
    
    if engine in ["openai", "azure"]:
        if not config.get("api_key") and not os.getenv("OPENAI_API_KEY") and not os.getenv("AZURE_OPENAI_API_KEY"):
            logger.error(f"❌ API key required for {engine} engine")
            raise ConfigurationError(f"API key required for {engine} engine")
    
    elif engine == "anthropic":
        if not config.get("api_key") and not os.getenv("ANTHROPIC_API_KEY"):
            logger.error("❌ API key required for Anthropic engine")
            raise ConfigurationError("API key required for Anthropic engine")
    
    elif engine == "local":
        if not config.get("endpoint"):
            config["endpoint"] = "http://localhost:11434/api/generate"  # Default to Ollama
            logger.debug("🔧 Set default endpoint for local engine")
    
    logger.debug(f"✅ Configuration validation successful for {engine}")
    return True


def _sanitize_config_for_logging(config: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize config for logging by masking sensitive data."""
    sanitized = config.copy()
    
    # Mask sensitive fields
    sensitive_fields = ['api_key', 'password', 'token', 'secret']
    for field in sensitive_fields:
        if field in sanitized and sanitized[field]:
            # Show first 4 and last 4 characters, mask the rest
            value = str(sanitized[field])
            if len(value) > 8:
                sanitized[field] = f"{value[:4]}...{value[-4:]}"
            else:
                sanitized[field] = "***"
    
    return sanitized 