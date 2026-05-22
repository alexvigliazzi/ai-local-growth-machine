"""Unit 3: Agent base class — error paths, prompt loading, run() logic."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestAgentPromptLoading:
    def test_missing_agent_md_returns_default_prompt(self):
        from agents.base import Agent

        agent = Agent("nonexistent_agent_xyz_12345", "fast")
        assert agent.system_prompt == "You are the nonexistent_agent_xyz_12345 agent."

    def test_agent_md_without_system_prompt_section(self, tmp_path):
        """Agent file exists but has no ## System Prompt heading."""
        md_file = tmp_path / "agent_nosection.md"
        md_file.write_text("# Agent NoSection\n\nJust some text without the right heading.\n", encoding="utf-8")

        from agents.base import Agent

        with patch("agents.base.AGENTS_DIR", str(tmp_path)):
            agent = Agent("nosection", "fast")

        assert agent.system_prompt == "You are the nosection agent."

    def test_agent_md_extracts_system_prompt_section(self):
        from agents.base import Agent

        agent = Agent("content_planner", "strong")
        assert agent.system_prompt  # non-empty
        assert len(agent.system_prompt) > 20  # real content, not just fallback

    def test_custom_system_prompt_overrides_file(self):
        from agents.base import Agent

        agent = Agent("researcher", "fast", system_prompt="Custom prompt here")
        assert agent.system_prompt == "Custom prompt here"


class TestAgentRun:
    @patch("agents.base.LLMRouter")
    def test_run_with_no_args_raises_value_error(self, mock_router_cls):
        from agents.base import Agent

        agent = Agent("test", "fast", system_prompt="sys")
        with pytest.raises(ValueError, match="Provide either"):
            agent.run()

    @patch("agents.base.LLMRouter")
    def test_run_with_user_prompt_uses_agent_system_prompt(self, mock_router_cls):
        mock_router = MagicMock()
        mock_router_cls.return_value = mock_router
        mock_router.generate.return_value = "result"

        from agents.base import Agent

        agent = Agent("test", "balanced", system_prompt="My system prompt")
        agent.run(user_prompt="Do something")

        call_args = mock_router.generate.call_args[0]
        assert call_args[0] == "My system prompt"
        assert call_args[1] == "Do something"

    @patch("agents.base._renderer")
    @patch("agents.base.LLMRouter")
    def test_run_with_template_uses_template_system_when_present(self, mock_router_cls, mock_renderer):
        """When template has a ## System section, it takes precedence over agent's system_prompt."""
        mock_renderer.render.return_value = ("template system", "template user")
        mock_router = MagicMock()
        mock_router_cls.return_value = mock_router
        mock_router.generate.return_value = "result"

        from agents.base import Agent

        agent = Agent("test", "strong", system_prompt="AGENT SYSTEM PROMPT")
        agent.run(template="content_plan", variables={"key": "val"})

        call_args = mock_router.generate.call_args[0]
        assert call_args[0] == "template system"  # template's system wins

    @patch("agents.base._renderer")
    @patch("agents.base.LLMRouter")
    def test_run_with_template_falls_back_to_agent_system_when_template_has_none(self, mock_router_cls, mock_renderer):
        """When template has no ## System section, agent's system_prompt is used as fallback."""
        mock_renderer.render.return_value = ("", "template user")  # empty system from template
        mock_router = MagicMock()
        mock_router_cls.return_value = mock_router
        mock_router.generate.return_value = "result"

        from agents.base import Agent

        agent = Agent("test", "strong", system_prompt="AGENT SYSTEM PROMPT")
        agent.run(template="content_plan", variables={"key": "val"})

        call_args = mock_router.generate.call_args[0]
        assert call_args[0] == "AGENT SYSTEM PROMPT"  # agent's system_prompt used as fallback

    @patch("agents.base.LLMRouter")
    def test_run_propagates_llm_router_exception(self, mock_router_cls):
        mock_router = MagicMock()
        mock_router_cls.return_value = mock_router
        mock_router.generate.side_effect = RuntimeError("All backends failed")

        from agents.base import Agent

        agent = Agent("test", "fast", system_prompt="sys")
        with pytest.raises(RuntimeError, match="All backends failed"):
            agent.run(user_prompt="Go")

    @patch("agents.base.LLMRouter")
    def test_run_with_empty_system_prompt(self, mock_router_cls):
        mock_router = MagicMock()
        mock_router_cls.return_value = mock_router
        mock_router.generate.return_value = "ok"

        from agents.base import Agent

        agent = Agent("test", "fast", system_prompt="")
        # empty string is falsy, so __init__ falls back to _load_system_prompt
        # but if file doesn't exist, it gets "You are the test agent."
        result = agent.run(user_prompt="Go")
        assert result == "ok"
