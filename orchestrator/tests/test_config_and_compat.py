"""Unit 7: Config validation and AiClient backward compatibility."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import importlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestConfigDefaults:
    def test_config_defaults_when_env_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("config.load_dotenv"):
                import config
                importlib.reload(config)

                assert config.RAILS_API_URL == "http://localhost:3000/api"
                assert config.API_TOKEN == ""
                assert config.OLLAMA_HOST == "http://localhost:11434"
                assert config.OLLAMA_MODEL == "gemma3:1b-it-qat"
                assert config.ANTHROPIC_API_KEY == ""
                assert config.LLM_DEFAULT_BACKEND == "ollama"

    def test_config_reads_custom_env_vars(self):
        custom_env = {
            "RAILS_API_URL": "http://custom:4000/api",
            "API_TOKEN": "secret-token-123",
            "OLLAMA_HOST": "http://gpu-server:11434",
            "ANTHROPIC_API_KEY": "sk-ant-test",
        }
        with patch.dict(os.environ, custom_env, clear=True):
            with patch("config.load_dotenv"):
                import config
                importlib.reload(config)

                assert config.RAILS_API_URL == "http://custom:4000/api"
                assert config.API_TOKEN == "secret-token-123"
                assert config.OLLAMA_HOST == "http://gpu-server:11434"
                assert config.ANTHROPIC_API_KEY == "sk-ant-test"


class TestConfigPaths:
    def test_prompts_dir_resolves_correctly(self):
        import config

        # Should end with automations/prompts (OS-independent)
        normalized = config.PROMPTS_DIR.replace("\\", "/")
        assert normalized.endswith("automations/prompts")

    def test_agents_dir_resolves_correctly(self):
        import config

        normalized = config.AGENTS_DIR.replace("\\", "/")
        assert normalized.endswith("automations/agents")


class TestClaudeBackendLazyValidation:
    @patch("ai_client.anthropic.Anthropic")
    def test_empty_anthropic_key_creates_backend_without_error(self, mock_anthropic_cls):
        """ClaudeBackend with empty key doesn't error at init — only on generate()."""
        from ai_client import ClaudeBackend

        # This should NOT raise
        backend = ClaudeBackend()
        assert backend is not None


class TestRailsClientEmptyToken:
    def test_empty_api_token_sends_empty_bearer(self):
        """BUG DOCUMENTATION: empty API_TOKEN sends 'Bearer ' header."""
        with patch("rails_client.API_TOKEN", ""):
            from rails_client import RailsClient

            client = RailsClient()
            assert client.headers["Authorization"] == "Bearer "


class TestAiClientBackwardCompat:
    @patch("ai_client.LLMRouter")
    def test_ai_client_uses_fast_profile(self, mock_router_cls):
        mock_router = MagicMock()
        mock_router_cls.return_value = mock_router
        mock_router.generate.return_value = "result"

        from ai_client import AiClient

        client = AiClient()
        client.generate("sys", "usr")

        mock_router_cls.assert_called_once_with(profile="fast")

    @patch("ai_client.LLMRouter")
    def test_ai_client_ignores_model_and_host(self, mock_router_cls):
        """BUG DOCUMENTATION: model and host params are dead code — stored but never used."""
        mock_router = MagicMock()
        mock_router_cls.return_value = mock_router
        mock_router.generate.return_value = "result"

        from ai_client import AiClient

        client = AiClient(model="gpt-4", host="http://other:8080")
        assert client._model == "gpt-4"
        assert client._host == "http://other:8080"

        client.generate("sys", "usr")

        # Despite passing model/host, router still uses "fast" profile
        mock_router_cls.assert_called_once_with(profile="fast")
