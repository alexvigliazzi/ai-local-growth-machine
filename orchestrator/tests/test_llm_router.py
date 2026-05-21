import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_client import LLMRouter, LLMBackend


class TestLLMBackend:
    def test_profiles_map_to_backends(self):
        assert LLMRouter.profile_to_backend("fast") == "ollama"
        assert LLMRouter.profile_to_backend("balanced") == "claude_haiku"
        assert LLMRouter.profile_to_backend("strong") == "claude_sonnet"
        assert LLMRouter.profile_to_backend("unknown") == "ollama"


class TestOllamaBackend:
    @patch("ai_client.ollama.Client")
    def test_generate_calls_ollama(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.chat.return_value = {"message": {"content": "test response"}}

        backend = LLMBackend.create("ollama")
        result = backend.generate("system prompt", "user prompt")

        assert result == "test response"
        mock_client.chat.assert_called_once()
        call_args = mock_client.chat.call_args
        messages = call_args[1]["messages"]
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"


class TestClaudeBackend:
    @patch("ai_client.anthropic.Anthropic")
    def test_generate_calls_claude(self, mock_anthropic_class):
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="claude response")]
        mock_client.messages.create.return_value = mock_response

        backend = LLMBackend.create("claude_haiku")
        result = backend.generate("system prompt", "user prompt")

        assert result == "claude response"
        mock_client.messages.create.assert_called_once()


class TestRouterFallback:
    @patch("ai_client.ollama.Client")
    @patch("ai_client.anthropic.Anthropic")
    def test_fallback_on_error(self, mock_anthropic_class, mock_ollama_client_class):
        # claude_haiku fails → falls back to ollama
        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic
        mock_anthropic.messages.create.side_effect = Exception("api error")

        mock_ollama = MagicMock()
        mock_ollama_client_class.return_value = mock_ollama
        mock_ollama.chat.return_value = {"message": {"content": "fallback response"}}

        router = LLMRouter(profile="balanced")  # balanced → claude_haiku → ollama
        result = router.generate("system", "user")

        assert result == "fallback response"
        mock_anthropic.messages.create.assert_called_once()
        mock_ollama.chat.assert_called_once()
