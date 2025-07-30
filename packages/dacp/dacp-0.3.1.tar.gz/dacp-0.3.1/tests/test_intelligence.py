"""
Tests for the intelligence module.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

from dacp.intelligence import (
    invoke_intelligence,
    IntelligenceError,
    UnsupportedProviderError,
    ConfigurationError,
    validate_config,
    get_supported_engines,
    _invoke_openai,
    _invoke_anthropic,
    _invoke_azure_openai,
    _invoke_local
)


class TestInvokeIntelligence:
    """Test the main invoke_intelligence function."""

    def test_missing_engine_raises_error(self):
        """Test that missing engine raises ConfigurationError."""
        config = {"model": "gpt-4"}
        with pytest.raises(ConfigurationError, match="Missing 'engine'"):
            invoke_intelligence("test prompt", config)

    def test_unsupported_engine_raises_error(self):
        """Test that unsupported engine raises UnsupportedProviderError."""
        config = {"engine": "unsupported_engine"}
        with pytest.raises(UnsupportedProviderError, match="Unsupported intelligence engine"):
            invoke_intelligence("test prompt", config)

    @patch('dacp.intelligence._invoke_openai')
    def test_openai_engine_calls_correct_function(self, mock_openai):
        """Test that OpenAI engine calls the correct function."""
        mock_openai.return_value = "OpenAI response"
        config = {"engine": "openai", "model": "gpt-4"}
        
        result = invoke_intelligence("test prompt", config)
        
        assert result == "OpenAI response"
        mock_openai.assert_called_once_with("test prompt", config)

    @patch('dacp.intelligence._invoke_anthropic')
    def test_anthropic_engine_calls_correct_function(self, mock_anthropic):
        """Test that Anthropic engine calls the correct function."""
        mock_anthropic.return_value = "Anthropic response"
        config = {"engine": "anthropic", "model": "claude-3-haiku-20240307"}
        
        result = invoke_intelligence("test prompt", config)
        
        assert result == "Anthropic response"
        mock_anthropic.assert_called_once_with("test prompt", config)

    @patch('dacp.intelligence._invoke_azure_openai')
    def test_azure_engine_calls_correct_function(self, mock_azure):
        """Test that Azure engine calls the correct function."""
        mock_azure.return_value = "Azure response"
        config = {"engine": "azure", "model": "gpt-4"}
        
        result = invoke_intelligence("test prompt", config)
        
        assert result == "Azure response"
        mock_azure.assert_called_once_with("test prompt", config)

    @patch('dacp.intelligence._invoke_local')
    def test_local_engine_calls_correct_function(self, mock_local):
        """Test that local engine calls the correct function."""
        mock_local.return_value = "Local response"
        config = {"engine": "local", "model": "llama2"}
        
        result = invoke_intelligence("test prompt", config)
        
        assert result == "Local response"
        mock_local.assert_called_once_with("test prompt", config)

    def test_engine_case_insensitive(self):
        """Test that engine names are case insensitive."""
        with patch('dacp.intelligence._invoke_openai') as mock_openai:
            mock_openai.return_value = "response"
            config = {"engine": "OPENAI", "model": "gpt-4"}
            invoke_intelligence("test", config)
            mock_openai.assert_called_once()


class TestOpenAIProvider:
    """Test the OpenAI provider."""

    @patch('dacp.intelligence.openai')
    def test_openai_success(self, mock_openai_module):
        """Test successful OpenAI call."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "OpenAI response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_module.OpenAI.return_value = mock_client
        
        config = {
            "model": "gpt-4",
            "api_key": "test-key",
            "endpoint": "https://api.openai.com/v1",
            "temperature": 0.5,
            "max_tokens": 100
        }
        
        result = _invoke_openai("test prompt", config)
        
        assert result == "OpenAI response"
        mock_openai_module.OpenAI.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.openai.com/v1"
        )

    @patch('dacp.intelligence.openai')
    def test_openai_missing_package(self, mock_openai_module):
        """Test OpenAI with missing package."""
        mock_openai_module.side_effect = ImportError()
        config = {"api_key": "test-key"}
        
        with pytest.raises(IntelligenceError, match="OpenAI package not installed"):
            _invoke_openai("test", config)

    def test_openai_missing_api_key(self):
        """Test OpenAI with missing API key."""
        config = {"model": "gpt-4"}
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError, match="OpenAI API key not found"):
                _invoke_openai("test", config)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"})
    @patch('dacp.intelligence.openai')
    def test_openai_uses_env_key(self, mock_openai_module):
        """Test OpenAI uses environment variable for API key."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_module.OpenAI.return_value = mock_client
        
        config = {"model": "gpt-4"}
        _invoke_openai("test", config)
        
        mock_openai_module.OpenAI.assert_called_once_with(
            api_key="env-key",
            base_url="https://api.openai.com/v1"
        )


class TestAnthropicProvider:
    """Test the Anthropic provider."""

    @patch('dacp.intelligence.anthropic')
    def test_anthropic_success(self, mock_anthropic_module):
        """Test successful Anthropic call."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Anthropic response"
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_module.Anthropic.return_value = mock_client
        
        config = {
            "model": "claude-3-haiku-20240307",
            "api_key": "test-key",
            "endpoint": "https://api.anthropic.com",
            "temperature": 0.5,
            "max_tokens": 100
        }
        
        result = _invoke_anthropic("test prompt", config)
        
        assert result == "Anthropic response"

    @patch('dacp.intelligence.anthropic')
    def test_anthropic_missing_package(self, mock_anthropic_module):
        """Test Anthropic with missing package."""
        mock_anthropic_module.side_effect = ImportError()
        config = {"api_key": "test-key"}
        
        with pytest.raises(IntelligenceError, match="Anthropic package not installed"):
            _invoke_anthropic("test", config)

    def test_anthropic_missing_api_key(self):
        """Test Anthropic with missing API key."""
        config = {"model": "claude-3-haiku-20240307"}
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError, match="Anthropic API key not found"):
                _invoke_anthropic("test", config)


class TestLocalProvider:
    """Test the local provider."""

    @patch('dacp.intelligence.requests')
    def test_local_ollama_success(self, mock_requests):
        """Test successful local Ollama call."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Local response"}
        mock_requests.post.return_value = mock_response
        
        config = {
            "endpoint": "http://localhost:11434/api/generate",
            "model": "llama2"
        }
        
        result = _invoke_local("test prompt", config)
        
        assert result == "Local response"

    @patch('dacp.intelligence.requests')
    def test_local_generic_success(self, mock_requests):
        """Test successful generic local API call."""
        mock_response = Mock()
        mock_response.json.return_value = {"text": "Generic response"}
        mock_requests.post.return_value = mock_response
        
        config = {
            "endpoint": "http://localhost:8080/generate",
            "model": "custom-model"
        }
        
        result = _invoke_local("test prompt", config)
        
        assert result == "Generic response"

    @patch('dacp.intelligence.requests')
    def test_local_request_error(self, mock_requests):
        """Test local provider request error."""
        mock_requests.post.side_effect = Exception("Connection error")
        
        config = {"endpoint": "http://localhost:11434/api/generate"}
        
        with pytest.raises(IntelligenceError, match="Local provider error"):
            _invoke_local("test", config)


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = {"engine": "openai", "model": "gpt-4", "api_key": "test-key"}
        assert validate_config(config) is True

    def test_validate_missing_engine(self):
        """Test validation with missing engine."""
        config = {"model": "gpt-4"}
        with pytest.raises(ConfigurationError, match="Missing 'engine'"):
            validate_config(config)

    def test_validate_unsupported_engine(self):
        """Test validation with unsupported engine."""
        config = {"engine": "unsupported"}
        with pytest.raises(ConfigurationError, match="Unsupported engine"):
            validate_config(config)

    def test_validate_non_dict_config(self):
        """Test validation with non-dictionary config."""
        with pytest.raises(ConfigurationError, match="Configuration must be a dictionary"):
            validate_config("not a dict")

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_openai_missing_key(self):
        """Test validation of OpenAI config without API key."""
        config = {"engine": "openai", "model": "gpt-4"}
        with pytest.raises(ConfigurationError, match="API key required"):
            validate_config(config)

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_anthropic_missing_key(self):
        """Test validation of Anthropic config without API key."""
        config = {"engine": "anthropic", "model": "claude-3-haiku-20240307"}
        with pytest.raises(ConfigurationError, match="API key required"):
            validate_config(config)

    def test_validate_local_sets_default_endpoint(self):
        """Test validation of local config sets default endpoint."""
        config = {"engine": "local", "model": "llama2"}
        validate_config(config)
        assert config["endpoint"] == "http://localhost:11434/api/generate"


def test_get_supported_engines():
    """Test getting supported engines."""
    engines = get_supported_engines()
    expected = ["openai", "anthropic", "azure", "local"]
    assert engines == expected 