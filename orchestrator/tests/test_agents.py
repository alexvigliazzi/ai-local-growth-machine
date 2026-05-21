import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.base import Agent


class TestAgentLoadDefinition:
    def test_loads_agent_md_file(self):
        agent = Agent(name="content_planner", profile="fast")
        assert "calendario" in agent.system_prompt.lower() or "content" in agent.system_prompt.lower()

    def test_custom_system_prompt_overrides_file(self):
        agent = Agent(name="custom", profile="fast", system_prompt="Custom system prompt")
        assert agent.system_prompt == "Custom system prompt"


class TestAgentRun:
    @patch("agents.base.LLMRouter")
    def test_run_calls_router_with_profile(self, mock_router_class):
        mock_router = MagicMock()
        mock_router_class.return_value = mock_router
        mock_router.generate.return_value = "generated content"

        agent = Agent(name="test", profile="balanced", system_prompt="You are a test agent")
        result = agent.run(user_prompt="Generate something")

        mock_router_class.assert_called_once_with(profile="balanced")
        mock_router.generate.assert_called_once_with("You are a test agent", "Generate something")
        assert result == "generated content"

    @patch("agents.base.LLMRouter")
    def test_run_with_template_variables(self, mock_router_class):
        mock_router = MagicMock()
        mock_router_class.return_value = mock_router
        mock_router.generate.return_value = "plan output"

        agent = Agent(name="test", profile="fast", system_prompt="You plan content")
        result = agent.run(
            template="content_plan",
            variables={"business_name": "Test Biz", "niche": "cafe", "city": "SP",
                       "services": "cafe", "tone": "informal", "objective": "engajamento",
                       "references": "", "target_audience": "jovens", "duration": "7"}
        )

        assert result == "plan output"
        mock_router.generate.assert_called_once()
        call_args = mock_router.generate.call_args[0]
        assert "Test Biz" in call_args[1] or "cafe" in call_args[1]
