import os
import re
from config import PROMPTS_DIR


class PromptRenderer:
    def __init__(self, prompts_dir=None):
        self.prompts_dir = prompts_dir or PROMPTS_DIR

    def render(self, template_name, variables):
        path = os.path.join(self.prompts_dir, f"{template_name}.md")
        with open(path, "r", encoding="utf-8") as f:
            template = f.read()

        sections = self._parse_sections(template)
        system_prompt = sections.get("system", "")
        user_prompt = sections.get("user", "")

        for key, value in variables.items():
            placeholder = "{" + key + "}"
            system_prompt = system_prompt.replace(placeholder, str(value))
            user_prompt = user_prompt.replace(placeholder, str(value))

        return system_prompt.strip(), user_prompt.strip()

    def _parse_sections(self, text):
        sections = {}
        current_section = None
        current_lines = []

        for line in text.split("\n"):
            header_match = re.match(r"^##\s+(.+)$", line)
            if header_match:
                if current_section:
                    sections[current_section] = "\n".join(current_lines)
                current_section = header_match.group(1).strip().lower()
                current_lines = []
            elif current_section:
                current_lines.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_lines)

        return sections
