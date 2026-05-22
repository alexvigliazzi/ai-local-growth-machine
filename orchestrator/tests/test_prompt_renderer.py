"""Unit 2: PromptRenderer — edge cases and parsing robustness."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _write_template(tmp_path, name, content):
    path = tmp_path / f"{name}.md"
    path.write_text(content, encoding="utf-8")
    return path


class TestRenderVariables:
    def test_render_replaces_all_variables(self, tmp_path):
        _write_template(tmp_path, "test", "## System\nHello {name} from {city}\n\n## User\nDo {task}")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {"name": "Ana", "city": "SP", "task": "analyze"})

        assert "Ana" in system
        assert "SP" in system
        assert "analyze" in user

    def test_render_unreplaced_variable_left_as_literal(self, tmp_path):
        _write_template(tmp_path, "test", "## System\nHello {name}\n\n## User\n{missing_var}")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {"name": "Ana"})

        assert "Ana" in system
        assert "{missing_var}" in user  # unreplaced placeholder stays

    def test_render_extra_variables_ignored(self, tmp_path):
        _write_template(tmp_path, "test", "## System\nHello {name}\n\n## User\nGo")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {"name": "Ana", "extra": "ignored", "unused": "too"})

        assert "Ana" in system  # no error from extra keys

    def test_render_none_value_becomes_string_none(self, tmp_path):
        """BUG DOCUMENTATION: None values become literal 'None' in prompts."""
        _write_template(tmp_path, "test", "## System\nRef: {references}\n\n## User\nGo")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {"references": None})

        assert "None" in system  # str(None) = "None" — pollutes LLM input

    def test_render_int_value_converted_to_string(self, tmp_path):
        _write_template(tmp_path, "test", "## System\nCount: {count}\n\n## User\nGo")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {"count": 42})

        assert "42" in system


class TestRenderEdgeCases:
    def test_render_missing_template_file_raises(self, tmp_path):
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        with pytest.raises(FileNotFoundError):
            renderer.render("nonexistent_template", {})

    def test_render_template_without_system_section(self, tmp_path):
        _write_template(tmp_path, "test", "## User\nOnly user content here")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {})

        assert system == ""
        assert "Only user content here" in user

    def test_render_template_without_user_section(self, tmp_path):
        _write_template(tmp_path, "test", "## System\nOnly system content here")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {})

        assert "Only system content here" in system
        assert user == ""

    def test_render_template_with_no_sections(self, tmp_path):
        """BUG DOCUMENTATION: content before first ## header is silently dropped."""
        _write_template(tmp_path, "test", "This is plain text\nNo sections here\nAll lost")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {})

        assert system == ""
        assert user == ""  # all content silently lost


class TestParseSections:
    def test_parse_sections_case_insensitive(self, tmp_path):
        _write_template(tmp_path, "test", "## SYSTEM\nUpper case\n\n## User\nMixed case")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {})

        assert "Upper case" in system
        assert "Mixed case" in user

    def test_parse_sections_preserves_multiline_content(self, tmp_path):
        _write_template(tmp_path, "test", "## System\nLine 1\nLine 2\nLine 3\n\n## User\nGo")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {})

        assert "Line 1" in system
        assert "Line 2" in system
        assert "Line 3" in system

    def test_parse_sections_ignores_h1_and_h3(self, tmp_path):
        _write_template(tmp_path, "test", "# Title\n## System\nContent\n### Sub\nMore\n\n## User\nGo")
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer(prompts_dir=str(tmp_path))
        system, user = renderer.render("test", {})

        # h1 and h3 should not create new sections; ### Sub stays inside system
        assert "Content" in system
        assert "More" in system


class TestRealTemplates:
    def test_render_with_real_content_plan_template(self):
        from prompt_renderer import PromptRenderer

        renderer = PromptRenderer()
        variables = {
            "duration": "7",
            "business_name": "Cafe Central",
            "niche": "cafeteria",
            "city": "Campinas",
            "services": "cafe, bolo",
            "target_audience": "jovens universitarios",
            "tone": "informal",
            "objective": "engajamento",
            "references": "",
        }
        system, user = renderer.render("content_plan", variables)

        assert system  # non-empty
        assert user  # non-empty
        assert "Cafe Central" in user or "Cafe Central" in system
        assert "{business_name}" not in user  # no unreplaced placeholders
        assert "{niche}" not in user
