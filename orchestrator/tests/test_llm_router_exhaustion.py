"""Unit 4: LLM Router exhaustion — full fallback chain and edge cases."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@patch("ai_client.anthropic.Anthropic")
@patch("ai_client.ollama.Client")
def test_three_level_fallback_sonnet_haiku_ollama(mock_ollama_cls, mock_anthropic_cls):
    """Sonnet fails, Haiku fails, Ollama succeeds."""
    mock_anthropic = MagicMock()
    mock_anthropic_cls.return_value = mock_anthropic
    mock_anthropic.messages.create.side_effect = Exception("Claude API down")

    mock_ollama = MagicMock()
    mock_ollama_cls.return_value = mock_ollama
    mock_ollama.chat.return_value = {"message": {"content": "ollama saved us"}}

    from ai_client import LLMRouter

    router = LLMRouter(profile="strong")  # claude_sonnet → claude_haiku → ollama
    result = router.generate("sys", "usr")

    assert result == "ollama saved us"
    # Anthropic called twice (sonnet + haiku), ollama called once
    assert mock_anthropic.messages.create.call_count == 2
    assert mock_ollama.chat.call_count == 1


@patch("ai_client.anthropic.Anthropic")
@patch("ai_client.ollama.Client")
def test_all_backends_fail_raises_runtime_error(mock_ollama_cls, mock_anthropic_cls):
    mock_anthropic = MagicMock()
    mock_anthropic_cls.return_value = mock_anthropic
    mock_anthropic.messages.create.side_effect = Exception("Claude down")

    mock_ollama = MagicMock()
    mock_ollama_cls.return_value = mock_ollama
    mock_ollama.chat.side_effect = Exception("Ollama down")

    from ai_client import LLMRouter

    router = LLMRouter(profile="strong")
    with pytest.raises(RuntimeError):
        router.generate("sys", "usr")


@patch("ai_client.anthropic.Anthropic")
@patch("ai_client.ollama.Client")
def test_all_backends_fail_message_includes_profile(mock_ollama_cls, mock_anthropic_cls):
    mock_anthropic = MagicMock()
    mock_anthropic_cls.return_value = mock_anthropic
    mock_anthropic.messages.create.side_effect = Exception("Claude down")

    mock_ollama = MagicMock()
    mock_ollama_cls.return_value = mock_ollama
    mock_ollama.chat.side_effect = Exception("Ollama down")

    from ai_client import LLMRouter

    router = LLMRouter(profile="strong")
    with pytest.raises(RuntimeError, match="strong"):
        router.generate("sys", "usr")


@patch("ai_client.anthropic.Anthropic")
@patch("ai_client.ollama.Client")
def test_all_backends_fail_message_includes_last_error(mock_ollama_cls, mock_anthropic_cls):
    mock_anthropic = MagicMock()
    mock_anthropic_cls.return_value = mock_anthropic
    mock_anthropic.messages.create.side_effect = Exception("Claude down")

    mock_ollama = MagicMock()
    mock_ollama_cls.return_value = mock_ollama
    mock_ollama.chat.side_effect = Exception("Ollama crashed hard")

    from ai_client import LLMRouter

    router = LLMRouter(profile="strong")
    with pytest.raises(RuntimeError, match="Ollama crashed hard"):
        router.generate("sys", "usr")


def test_unknown_backend_name_raises_value_error():
    from ai_client import LLMBackend

    with pytest.raises(ValueError, match="Unknown backend"):
        LLMBackend.create("gpt4")


def test_unknown_profile_uses_default_backend():
    from ai_client import LLMRouter

    router = LLMRouter(profile="nonexistent_profile")
    # Should map to LLM_DEFAULT_BACKEND (ollama)
    assert router.backend_name == "ollama"


@patch("ai_client.ollama.Client")
def test_ollama_no_fallback_fails_immediately(mock_ollama_cls):
    mock_ollama = MagicMock()
    mock_ollama_cls.return_value = mock_ollama
    mock_ollama.chat.side_effect = Exception("Ollama down")

    from ai_client import LLMRouter

    router = LLMRouter(profile="fast")  # ollama, no fallback
    with pytest.raises(RuntimeError, match="fast"):
        router.generate("sys", "usr")

    assert mock_ollama.chat.call_count == 1  # only one attempt


@patch("ai_client.anthropic.Anthropic")
@patch("ai_client.ollama.Client")
def test_first_backend_succeeds_no_fallback(mock_ollama_cls, mock_anthropic_cls):
    mock_anthropic = MagicMock()
    mock_anthropic_cls.return_value = mock_anthropic
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="sonnet response")]
    mock_anthropic.messages.create.return_value = mock_response

    from ai_client import LLMRouter

    router = LLMRouter(profile="strong")  # claude_sonnet
    result = router.generate("sys", "usr")

    assert result == "sonnet response"
    assert mock_ollama_cls.call_count == 0  # ollama never instantiated
