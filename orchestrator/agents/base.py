import os
import re
from ai_client import LLMRouter
from prompt_renderer import PromptRenderer
from config import AGENTS_DIR

_renderer = PromptRenderer()


class Agent:
    def __init__(self, name: str, profile: str, system_prompt: str = None):
        self.name = name
        self.profile = profile
        self.system_prompt = system_prompt or self._load_system_prompt(name)

    def run(self, user_prompt: str = None, template: str = None, variables: dict = None) -> str:
        router = LLMRouter(profile=self.profile)

        if template and variables:
            system, user = _renderer.render(template, variables)
            if not system and self.system_prompt:
                system = self.system_prompt
        elif user_prompt:
            system = self.system_prompt
            user = user_prompt
        else:
            raise ValueError("Provide either user_prompt or template+variables")

        return router.generate(system, user)

    def _load_system_prompt(self, name: str) -> str:
        agent_file = os.path.join(AGENTS_DIR, f"agent_{name}.md")
        if not os.path.exists(agent_file):
            return f"You are the {name} agent."

        with open(agent_file, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r"## System Prompt\s*\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return f"You are the {name} agent."
