# Agent Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve the flat Ollama-only orchestrator into a multi-backend agent system with LLM routing, composable agents, and multi-step workflows.

**Architecture:** Each agent is a Python class that wraps a system prompt, input/output schema, and an LLM router profile. The LLM Router selects the backend (Ollama local, Claude API, or Gemini) based on the profile. Workflows compose agents into pipelines — content_generation chains researcher → planner → video_script, lead_outreach chains researcher → copywriter, and weekly_report uses reporter directly.

**Tech Stack:** Python 3.11+, anthropic SDK (Claude API), ollama SDK (local), existing Rails API. No LangGraph for now — plain Python pipelines are sufficient for the current sequential workflows and avoid unnecessary complexity. Can migrate to LangGraph later if conditional branching or parallel execution is needed.

---

## File Structure

```
orchestrator/
├── config.py                    # (modify) Add Claude API key, Gemini config, router defaults
├── ai_client.py                 # (replace) Multi-backend LLM router
├── agents/
│   ├── __init__.py
│   ├── base.py                  # Agent base class
│   ├── researcher.py            # Research agent (niche analysis)
│   ├── content_planner.py       # Calendar planning agent
│   ├── copywriter.py            # Outreach message agent
│   ├── video_scripter.py        # Video script agent
│   └── reporter.py              # Weekly report agent
├── workflows/
│   ├── __init__.py
│   ├── content_generation.py    # researcher → planner → video_script pipeline
│   ├── lead_outreach.py         # researcher → copywriter pipeline
│   └── weekly_report.py         # reporter pipeline
├── tasks/
│   ├── __init__.py
│   ├── generate_content.py      # (modify) Use workflow instead of flat loop
│   ├── generate_outreach.py     # (modify) Use workflow instead of flat loop
│   └── generate_reports.py      # (modify) Use workflow instead of flat loop
├── prompt_renderer.py           # (keep as-is)
├── rails_client.py              # (keep as-is)
├── run.py                       # (keep as-is)
├── scheduler.py                 # (keep as-is)
├── requirements.txt             # (modify) Add anthropic SDK
├── .env.example                 # New: env var template
└── tests/
    ├── __init__.py
    ├── test_llm_router.py
    ├── test_agents.py
    └── test_workflows.py
```

---

### Task 1: Environment Setup and LLM Router Config

**Files:**
- Modify: `orchestrator/config.py`
- Modify: `orchestrator/requirements.txt`
- Create: `orchestrator/.env.example`

- [ ] **Step 1: Update requirements.txt**

```txt
ollama>=0.4
requests>=2.31
pyyaml>=6.0
schedule>=1.2
anthropic>=0.52
python-dotenv>=1.0
pytest>=8.0
```

- [ ] **Step 2: Create .env.example**

```env
# Rails API
RAILS_API_URL=http://localhost:3000/api
API_TOKEN=

# Ollama (local LLM)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:1b-it-qat

# Claude API (remote LLM)
ANTHROPIC_API_KEY=
CLAUDE_HAIKU_MODEL=claude-haiku-4-5-20251001
CLAUDE_SONNET_MODEL=claude-sonnet-4-6-20250514

# LLM Router defaults
LLM_DEFAULT_BACKEND=ollama
```

- [ ] **Step 3: Update config.py to load all backends**

```python
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

RAILS_API_URL = os.environ.get("RAILS_API_URL", "http://localhost:3000/api")
API_TOKEN = os.environ.get("API_TOKEN", "")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:1b-it-qat")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_HAIKU_MODEL = os.environ.get("CLAUDE_HAIKU_MODEL", "claude-haiku-4-5-20251001")
CLAUDE_SONNET_MODEL = os.environ.get("CLAUDE_SONNET_MODEL", "claude-sonnet-4-6-20250514")

LLM_DEFAULT_BACKEND = os.environ.get("LLM_DEFAULT_BACKEND", "ollama")

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "automations", "prompts")
AGENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "automations", "agents")
```

- [ ] **Step 4: Install updated dependencies**

Run: `cd orchestrator && pip install -r requirements.txt`
Expected: All packages install successfully, including `anthropic` and `python-dotenv`.

- [ ] **Step 5: Commit**

```bash
git add orchestrator/config.py orchestrator/requirements.txt orchestrator/.env.example
git commit -m "feat(orchestrator): add multi-backend config and Claude API dependency"
```

---

### Task 2: Multi-Backend LLM Router

**Files:**
- Replace: `orchestrator/ai_client.py`
- Create: `orchestrator/tests/__init__.py`
- Create: `orchestrator/tests/test_llm_router.py`

- [ ] **Step 1: Write tests for LLM router**

Create `orchestrator/tests/__init__.py` (empty file).

Create `orchestrator/tests/test_llm_router.py`:

```python
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
    def test_fallback_on_error(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.chat.side_effect = [
            Exception("connection refused"),
            {"message": {"content": "fallback response"}},
        ]

        router = LLMRouter(profile="fast")
        result = router.generate("system", "user")

        assert result == "fallback response"
        assert mock_client.chat.call_count == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd orchestrator && python -m pytest tests/test_llm_router.py -v`
Expected: FAIL — `LLMRouter`, `LLMBackend` not found.

- [ ] **Step 3: Implement LLM router**

Replace `orchestrator/ai_client.py`:

```python
import ollama
import anthropic
from config import (
    OLLAMA_HOST, OLLAMA_MODEL,
    ANTHROPIC_API_KEY, CLAUDE_HAIKU_MODEL, CLAUDE_SONNET_MODEL,
    LLM_DEFAULT_BACKEND,
)

PROFILE_MAP = {
    "fast": "ollama",
    "balanced": "claude_haiku",
    "strong": "claude_sonnet",
    "web-research": "claude_sonnet",
}

FALLBACK_CHAIN = {
    "claude_sonnet": ["claude_haiku", "ollama"],
    "claude_haiku": ["ollama"],
    "ollama": [],
}


class LLMBackend:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    @staticmethod
    def create(backend_name: str) -> "LLMBackend":
        if backend_name == "ollama":
            return OllamaBackend()
        elif backend_name == "claude_haiku":
            return ClaudeBackend(model=CLAUDE_HAIKU_MODEL)
        elif backend_name == "claude_sonnet":
            return ClaudeBackend(model=CLAUDE_SONNET_MODEL)
        raise ValueError(f"Unknown backend: {backend_name}")


class OllamaBackend(LLMBackend):
    def __init__(self, model=None, host=None):
        self.model = model or OLLAMA_MODEL
        self.client = ollama.Client(host=host or OLLAMA_HOST)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response["message"]["content"]


class ClaudeBackend(LLMBackend):
    def __init__(self, model=None):
        self.model = model or CLAUDE_HAIKU_MODEL
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text


class LLMRouter:
    def __init__(self, profile: str = "fast"):
        self.profile = profile
        self.backend_name = self.profile_to_backend(profile)

    @staticmethod
    def profile_to_backend(profile: str) -> str:
        return PROFILE_MAP.get(profile, LLM_DEFAULT_BACKEND)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        chain = [self.backend_name] + FALLBACK_CHAIN.get(self.backend_name, [])

        last_error = None
        for name in chain:
            try:
                backend = LLMBackend.create(name)
                return backend.generate(system_prompt, user_prompt)
            except Exception as e:
                print(f"  [{name}] failed: {e}, trying fallback...")
                last_error = e

        raise RuntimeError(f"All backends failed for profile '{self.profile}': {last_error}")


# Backward-compatible alias
class AiClient:
    def __init__(self, model=None, host=None):
        self._model = model
        self._host = host

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        router = LLMRouter(profile="fast")
        return router.generate(system_prompt, user_prompt)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd orchestrator && python -m pytest tests/test_llm_router.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add orchestrator/ai_client.py orchestrator/tests/
git commit -m "feat(orchestrator): multi-backend LLM router with fallback chain"
```

---

### Task 3: Agent Base Class

**Files:**
- Create: `orchestrator/agents/__init__.py`
- Create: `orchestrator/agents/base.py`
- Create: `orchestrator/tests/test_agents.py`

- [ ] **Step 1: Write tests for base agent**

Create `orchestrator/tests/test_agents.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd orchestrator && python -m pytest tests/test_agents.py -v`
Expected: FAIL — `agents.base` not found.

- [ ] **Step 3: Implement agent base class**

Create `orchestrator/agents/__init__.py`:

```python
from agents.base import Agent
```

Create `orchestrator/agents/base.py`:

```python
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
            if self.system_prompt and not template:
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd orchestrator && python -m pytest tests/test_agents.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add orchestrator/agents/
git commit -m "feat(orchestrator): agent base class with auto-loaded system prompts"
```

---

### Task 4: Concrete Agent Classes

**Files:**
- Create: `orchestrator/agents/researcher.py`
- Create: `orchestrator/agents/content_planner.py`
- Create: `orchestrator/agents/copywriter.py`
- Create: `orchestrator/agents/video_scripter.py`
- Create: `orchestrator/agents/reporter.py`

Each concrete agent is thin — it sets the right profile and exposes a typed `run()` method with the expected input parameters.

- [ ] **Step 1: Create researcher agent**

Create `orchestrator/agents/researcher.py`:

```python
from agents.base import Agent


class ResearcherAgent(Agent):
    def __init__(self):
        super().__init__(name="researcher", profile="strong")

    def research(self, business_name: str, niche: str, city: str, services: str = "", instagram_url: str = "") -> str:
        prompt = (
            f"Analise o seguinte negocio local e entregue um diagnostico completo:\n\n"
            f"**Negocio:** {business_name}\n"
            f"**Nicho:** {niche}\n"
            f"**Cidade:** {city}\n"
            f"**Servicos:** {services}\n"
            f"**Instagram:** {instagram_url}\n\n"
            f"Entregue: dores do publico-alvo, oportunidades de conteudo, angulos de conteudo, "
            f"concorrentes locais e proposta de posicionamento."
        )
        return self.run(user_prompt=prompt)
```

- [ ] **Step 2: Create content planner agent**

Create `orchestrator/agents/content_planner.py`:

```python
from agents.base import Agent


class ContentPlannerAgent(Agent):
    def __init__(self):
        super().__init__(name="content_planner", profile="strong")

    def plan(self, client: dict, request: dict, research_context: str = "") -> str:
        variables = {
            "business_name": client["business_name"],
            "niche": client["niche"],
            "city": client["city"],
            "services": request.get("services") or "",
            "tone": request.get("tone") or "profissional",
            "objective": request.get("objective") or "",
            "references": request.get("references") or "",
            "target_audience": f"Publico local de {client['city']} interessado em {client['niche']}",
            "duration": "7",
        }

        if research_context:
            variables["references"] = (
                f"{variables['references']}\n\n--- Contexto da pesquisa ---\n{research_context}"
            )

        return self.run(template="content_plan", variables=variables)
```

- [ ] **Step 3: Create video scripter agent**

Create `orchestrator/agents/video_scripter.py`:

```python
from agents.base import Agent


class VideoScripterAgent(Agent):
    def __init__(self):
        super().__init__(name="video_script", profile="strong")

    def script(self, client: dict, request: dict, themes: str = "") -> str:
        variables = {
            "business_name": client["business_name"],
            "niche": client["niche"],
            "tone": request.get("tone") or "profissional",
            "themes": themes or request.get("objective") or "conteudo do negocio",
            "count": "3",
            "duration": "35",
            "number": "1",
        }
        return self.run(template="video_script", variables=variables)
```

- [ ] **Step 4: Create copywriter agent**

Create `orchestrator/agents/copywriter.py`:

```python
from agents.base import Agent


class CopywriterAgent(Agent):
    def __init__(self):
        super().__init__(name="copywriter", profile="balanced")

    def write(self, lead: dict, channel: str, message_type: str, research_context: str = "") -> str:
        variables = {
            "business_name": lead["business_name"],
            "niche": lead["niche"],
            "city": lead["city"],
            "channel": channel,
            "instagram_url": lead.get("instagram_url") or "",
            "notes": lead.get("notes") or "",
            "message_type": message_type,
        }

        if research_context:
            variables["notes"] = (
                f"{variables['notes']}\n\n--- Contexto da pesquisa ---\n{research_context}"
            )

        return self.run(template="outreach_message", variables=variables)
```

- [ ] **Step 5: Create reporter agent**

Create `orchestrator/agents/reporter.py`:

```python
from agents.base import Agent


class ReporterAgent(Agent):
    def __init__(self):
        super().__init__(name="reporter", profile="balanced")

    def report(self, client: dict, period_start: str, period_end: str,
               outputs_summary: str, metrics: str = "") -> str:
        variables = {
            "business_name": client["business_name"],
            "niche": client["niche"],
            "plan": client.get("plan") or "starter",
            "period_start": period_start,
            "period_end": period_end,
            "content_outputs_summary": outputs_summary,
            "metrics": metrics or "Sem metricas disponiveis neste periodo.",
        }
        return self.run(template="weekly_report", variables=variables)
```

- [ ] **Step 6: Update agents/__init__.py to export all**

```python
from agents.base import Agent
from agents.researcher import ResearcherAgent
from agents.content_planner import ContentPlannerAgent
from agents.copywriter import CopywriterAgent
from agents.video_scripter import VideoScripterAgent
from agents.reporter import ReporterAgent
```

- [ ] **Step 7: Commit**

```bash
git add orchestrator/agents/
git commit -m "feat(orchestrator): concrete agent classes for all 5 agents"
```

---

### Task 5: Content Generation Workflow

**Files:**
- Create: `orchestrator/workflows/__init__.py`
- Create: `orchestrator/workflows/content_generation.py`
- Create: `orchestrator/tests/test_workflows.py`

- [ ] **Step 1: Write test for content generation workflow**

Create `orchestrator/tests/test_workflows.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestContentGenerationWorkflow:
    @patch("workflows.content_generation.VideoScripterAgent")
    @patch("workflows.content_generation.ContentPlannerAgent")
    @patch("workflows.content_generation.ResearcherAgent")
    def test_pipeline_runs_all_agents(self, mock_researcher_cls, mock_planner_cls, mock_scripter_cls):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher
        mock_researcher.research.return_value = "research output"

        mock_planner = MagicMock()
        mock_planner_cls.return_value = mock_planner
        mock_planner.plan.return_value = "content plan output"

        mock_scripter = MagicMock()
        mock_scripter_cls.return_value = mock_scripter
        mock_scripter.script.return_value = "video script output"

        from workflows.content_generation import ContentGenerationWorkflow

        client = {"business_name": "Test", "niche": "cafe", "city": "SP"}
        request = {"objective": "engajamento", "services": "cafe", "tone": "informal", "references": ""}

        workflow = ContentGenerationWorkflow()
        results = workflow.run(client=client, request=request)

        mock_researcher.research.assert_called_once()
        mock_planner.plan.assert_called_once()
        mock_scripter.script.assert_called_once()

        assert results["research"] == "research output"
        assert results["content_plan"] == "content plan output"
        assert results["video_script"] == "video script output"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd orchestrator && python -m pytest tests/test_workflows.py -v`
Expected: FAIL — `workflows.content_generation` not found.

- [ ] **Step 3: Implement content generation workflow**

Create `orchestrator/workflows/__init__.py` (empty file).

Create `orchestrator/workflows/content_generation.py`:

```python
from agents.researcher import ResearcherAgent
from agents.content_planner import ContentPlannerAgent
from agents.video_scripter import VideoScripterAgent


class ContentGenerationWorkflow:
    def run(self, client: dict, request: dict) -> dict:
        results = {}

        print(f"  [1/3] Researching: {client['business_name']}...")
        researcher = ResearcherAgent()
        results["research"] = researcher.research(
            business_name=client["business_name"],
            niche=client["niche"],
            city=client["city"],
            services=request.get("services") or "",
        )

        print(f"  [2/3] Planning content...")
        planner = ContentPlannerAgent()
        results["content_plan"] = planner.plan(
            client=client,
            request=request,
            research_context=results["research"],
        )

        print(f"  [3/3] Writing video scripts...")
        scripter = VideoScripterAgent()
        results["video_script"] = scripter.script(
            client=client,
            request=request,
            themes=request.get("objective") or "",
        )

        return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd orchestrator && python -m pytest tests/test_workflows.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add orchestrator/workflows/
git commit -m "feat(orchestrator): content generation workflow (researcher → planner → scripter)"
```

---

### Task 6: Lead Outreach Workflow

**Files:**
- Create: `orchestrator/workflows/lead_outreach.py`
- Modify: `orchestrator/tests/test_workflows.py`

- [ ] **Step 1: Write test for lead outreach workflow**

Append to `orchestrator/tests/test_workflows.py`:

```python
class TestLeadOutreachWorkflow:
    @patch("workflows.lead_outreach.CopywriterAgent")
    @patch("workflows.lead_outreach.ResearcherAgent")
    def test_pipeline_runs_researcher_then_copywriter(self, mock_researcher_cls, mock_copywriter_cls):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher
        mock_researcher.research.return_value = "lead research"

        mock_copywriter = MagicMock()
        mock_copywriter_cls.return_value = mock_copywriter
        mock_copywriter.write.return_value = "outreach message"

        from workflows.lead_outreach import LeadOutreachWorkflow

        lead = {"business_name": "Biz", "niche": "motos", "city": "BH",
                "instagram_url": "", "notes": ""}

        workflow = LeadOutreachWorkflow()
        result = workflow.run(lead=lead, channel="whatsapp", message_type="primeiro_contato")

        mock_researcher.research.assert_called_once()
        mock_copywriter.write.assert_called_once()
        assert result["message"] == "outreach message"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd orchestrator && python -m pytest tests/test_workflows.py::TestLeadOutreachWorkflow -v`
Expected: FAIL.

- [ ] **Step 3: Implement lead outreach workflow**

Create `orchestrator/workflows/lead_outreach.py`:

```python
from agents.researcher import ResearcherAgent
from agents.copywriter import CopywriterAgent


class LeadOutreachWorkflow:
    def run(self, lead: dict, channel: str, message_type: str) -> dict:
        results = {}

        print(f"  [1/2] Researching lead: {lead['business_name']}...")
        researcher = ResearcherAgent()
        results["research"] = researcher.research(
            business_name=lead["business_name"],
            niche=lead["niche"],
            city=lead["city"],
            instagram_url=lead.get("instagram_url") or "",
        )

        print(f"  [2/2] Writing {message_type} for {channel}...")
        copywriter = CopywriterAgent()
        results["message"] = copywriter.write(
            lead=lead,
            channel=channel,
            message_type=message_type,
            research_context=results["research"],
        )

        return results
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd orchestrator && python -m pytest tests/test_workflows.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add orchestrator/workflows/lead_outreach.py orchestrator/tests/test_workflows.py
git commit -m "feat(orchestrator): lead outreach workflow (researcher → copywriter)"
```

---

### Task 7: Weekly Report Workflow

**Files:**
- Create: `orchestrator/workflows/weekly_report.py`
- Modify: `orchestrator/tests/test_workflows.py`

- [ ] **Step 1: Write test for weekly report workflow**

Append to `orchestrator/tests/test_workflows.py`:

```python
class TestWeeklyReportWorkflow:
    @patch("workflows.weekly_report.ReporterAgent")
    def test_pipeline_runs_reporter(self, mock_reporter_cls):
        mock_reporter = MagicMock()
        mock_reporter_cls.return_value = mock_reporter
        mock_reporter.report.return_value = "report content"

        from workflows.weekly_report import WeeklyReportWorkflow

        client = {"business_name": "Biz", "niche": "cafe", "plan": "starter"}

        workflow = WeeklyReportWorkflow()
        result = workflow.run(
            client=client,
            period_start="14/05/2026",
            period_end="21/05/2026",
            outputs_summary="- Post 1 (social_post) — approved",
        )

        mock_reporter.report.assert_called_once()
        assert result["report"] == "report content"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd orchestrator && python -m pytest tests/test_workflows.py::TestWeeklyReportWorkflow -v`
Expected: FAIL.

- [ ] **Step 3: Implement weekly report workflow**

Create `orchestrator/workflows/weekly_report.py`:

```python
from agents.reporter import ReporterAgent


class WeeklyReportWorkflow:
    def run(self, client: dict, period_start: str, period_end: str,
            outputs_summary: str, metrics: str = "") -> dict:
        print(f"  [1/1] Generating report for: {client['business_name']}...")
        reporter = ReporterAgent()
        report = reporter.report(
            client=client,
            period_start=period_start,
            period_end=period_end,
            outputs_summary=outputs_summary,
            metrics=metrics,
        )
        return {"report": report}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd orchestrator && python -m pytest tests/test_workflows.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add orchestrator/workflows/weekly_report.py orchestrator/tests/test_workflows.py
git commit -m "feat(orchestrator): weekly report workflow"
```

---

### Task 8: Rewire Tasks to Use Workflows

**Files:**
- Modify: `orchestrator/tasks/generate_content.py`
- Modify: `orchestrator/tasks/generate_outreach.py`
- Modify: `orchestrator/tasks/generate_reports.py`

- [ ] **Step 1: Rewrite generate_content.py to use workflow**

```python
"""Fetch pending content requests, run the content generation workflow, post results to Rails."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rails_client import RailsClient
from workflows.content_generation import ContentGenerationWorkflow


def run():
    rails = RailsClient()
    workflow = ContentGenerationWorkflow()

    pending = rails.get_pending_content_requests()
    if not pending:
        print("No pending content requests.")
        return

    for req in pending:
        client = req["client"]
        print(f"Processing: {client['business_name']} — {req['objective']}")

        rails.mark_content_request_in_progress(req["id"])

        try:
            results = workflow.run(client=client, request=req)

            for output_type in ("content_plan", "video_script"):
                if output_type in results:
                    title = f"{output_type.replace('_', ' ').title()} — {client['business_name']}"
                    rails.create_content_output(req["id"], title, results[output_type], output_type)
                    print(f"  Created: {title}")

            rails.mark_content_request_completed(req["id"])
            print(f"  Completed: {req['id']}")
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    run()
```

- [ ] **Step 2: Rewrite generate_outreach.py to use workflow**

```python
"""Generate outreach messages using the lead outreach workflow."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rails_client import RailsClient
from workflows.lead_outreach import LeadOutreachWorkflow


def run():
    rails = RailsClient()
    workflow = LeadOutreachWorkflow()

    processed = 0

    queued = rails.get_queued_outreach_messages()
    for msg in queued:
        lead = rails.get_lead(msg["lead_id"])
        print(f"Processing: {lead['business_name']} via {msg['channel']}")

        try:
            results = workflow.run(
                lead=lead,
                channel=msg["channel"],
                message_type=msg["message_type"],
            )
            rails.fill_outreach_message(msg["id"], results["message"])
            print(f"  Done: {lead['business_name']}")
            processed += 1
        except Exception as e:
            print(f"  Error: {e}")

    if not queued:
        print("No queued messages from admin UI.")

    print(f"\nProcessed {processed} message(s).")


if __name__ == "__main__":
    run()
```

- [ ] **Step 3: Rewrite generate_reports.py to use workflow**

```python
"""Generate weekly reports using the weekly report workflow."""

import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rails_client import RailsClient
from workflows.weekly_report import WeeklyReportWorkflow


def run():
    rails = RailsClient()
    workflow = WeeklyReportWorkflow()

    clients = rails.get_clients(status="active")
    if not clients:
        print("No active clients.")
        return

    today = datetime.now()
    week_ago = today - timedelta(days=7)

    for client in clients:
        print(f"Generating report for: {client['business_name']}")

        details = rails.get_client_with_summary(client["id"])
        weekly_outputs = details.get("weekly_outputs", [])

        if not weekly_outputs:
            print(f"  No outputs this week, skipping.")
            continue

        outputs_summary = "\n".join(
            f"- {o['title']} ({o['output_type']}) — {o['status']}"
            for o in weekly_outputs
        )

        try:
            results = workflow.run(
                client=client,
                period_start=week_ago.strftime("%d/%m/%Y"),
                period_end=today.strftime("%d/%m/%Y"),
                outputs_summary=outputs_summary,
            )

            title = f"Relatorio Semanal — {client['business_name']} — {today.strftime('%d/%m/%Y')}"
            result = rails.create_report(client["id"], title, results["report"])
            print(f"  Created report (token: {result['token']})")
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    run()
```

- [ ] **Step 4: Run all tests**

Run: `cd orchestrator && python -m pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add orchestrator/tasks/
git commit -m "feat(orchestrator): rewire tasks to use agent workflows"
```

---

### Task 9: Social Post Agent (missing from workflows)

The content plan template exists (`social_post.md`) but there's no agent for it in the workflow. The content generation workflow should also produce social posts.

**Files:**
- Create: `orchestrator/agents/social_poster.py`
- Modify: `orchestrator/workflows/content_generation.py`
- Modify: `orchestrator/agents/__init__.py`

- [ ] **Step 1: Create social poster agent**

Create `orchestrator/agents/social_poster.py`:

```python
from agents.base import Agent


class SocialPosterAgent(Agent):
    def __init__(self):
        super().__init__(name="social_poster", profile="balanced",
                         system_prompt="Voce cria legendas de posts para Instagram de negocios locais brasileiros. "
                                       "Suas legendas sao curtas, diretas e com CTAs claros.")

    def post(self, client: dict, request: dict, themes: str = "") -> str:
        variables = {
            "business_name": client["business_name"],
            "niche": client["niche"],
            "city": client["city"],
            "tone": request.get("tone") or "profissional",
            "themes": themes or request.get("objective") or "conteudo do negocio",
            "format": "reels",
            "count": "3",
            "number": "1",
        }
        return self.run(template="social_post", variables=variables)
```

- [ ] **Step 2: Add social_poster to agents/__init__.py**

```python
from agents.base import Agent
from agents.researcher import ResearcherAgent
from agents.content_planner import ContentPlannerAgent
from agents.copywriter import CopywriterAgent
from agents.video_scripter import VideoScripterAgent
from agents.reporter import ReporterAgent
from agents.social_poster import SocialPosterAgent
```

- [ ] **Step 3: Add social poster step to content generation workflow**

Update `orchestrator/workflows/content_generation.py`:

```python
from agents.researcher import ResearcherAgent
from agents.content_planner import ContentPlannerAgent
from agents.video_scripter import VideoScripterAgent
from agents.social_poster import SocialPosterAgent


class ContentGenerationWorkflow:
    def run(self, client: dict, request: dict) -> dict:
        results = {}

        print(f"  [1/4] Researching: {client['business_name']}...")
        researcher = ResearcherAgent()
        results["research"] = researcher.research(
            business_name=client["business_name"],
            niche=client["niche"],
            city=client["city"],
            services=request.get("services") or "",
        )

        print(f"  [2/4] Planning content...")
        planner = ContentPlannerAgent()
        results["content_plan"] = planner.plan(
            client=client,
            request=request,
            research_context=results["research"],
        )

        print(f"  [3/4] Writing social posts...")
        poster = SocialPosterAgent()
        results["social_post"] = poster.post(
            client=client,
            request=request,
            themes=request.get("objective") or "",
        )

        print(f"  [4/4] Writing video scripts...")
        scripter = VideoScripterAgent()
        results["video_script"] = scripter.script(
            client=client,
            request=request,
            themes=request.get("objective") or "",
        )

        return results
```

- [ ] **Step 4: Update generate_content.py to include social_post output type**

In `orchestrator/tasks/generate_content.py`, change the output types loop:

```python
            for output_type in ("content_plan", "social_post", "video_script"):
```

- [ ] **Step 5: Run all tests**

Run: `cd orchestrator && python -m pytest tests/ -v`
Expected: All tests PASS (the workflow test mocks the new agent too — update test if needed).

- [ ] **Step 6: Commit**

```bash
git add orchestrator/agents/ orchestrator/workflows/content_generation.py orchestrator/tasks/generate_content.py
git commit -m "feat(orchestrator): add social post agent to content generation pipeline"
```

---

### Task 10: End-to-End Smoke Test

**Files:**
- Create: `orchestrator/tests/test_smoke.py`

- [ ] **Step 1: Write smoke test that validates the full stack with mocked backends**

Create `orchestrator/tests/test_smoke.py`:

```python
"""Smoke test: validates generate_content task with fully mocked Rails + LLM."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@patch("ai_client.anthropic.Anthropic")
@patch("ai_client.ollama.Client")
@patch("rails_client.requests")
def test_generate_content_end_to_end(mock_requests, mock_ollama_cls, mock_anthropic_cls):
    mock_ollama = MagicMock()
    mock_ollama_cls.return_value = mock_ollama
    mock_ollama.chat.return_value = {"message": {"content": "ollama output"}}

    mock_anthropic = MagicMock()
    mock_anthropic_cls.return_value = mock_anthropic
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="claude output")]
    mock_anthropic.messages.create.return_value = mock_response

    pending_response = MagicMock()
    pending_response.json.return_value = [{
        "id": "req-1",
        "objective": "engajamento",
        "services": "cafe, bolo",
        "tone": "informal",
        "references": "",
        "client": {
            "id": "cli-1",
            "business_name": "Cafe Central",
            "niche": "cafeteria",
            "city": "Campinas",
            "plan": "starter",
        },
    }]
    pending_response.raise_for_status = MagicMock()

    update_response = MagicMock()
    update_response.json.return_value = {"id": "req-1", "status": "in_progress"}
    update_response.raise_for_status = MagicMock()

    create_response = MagicMock()
    create_response.json.return_value = {"id": "out-1", "status": "draft"}
    create_response.raise_for_status = MagicMock()
    create_response.status_code = 201

    def route_requests(url, **kwargs):
        if "status=pending" in str(kwargs.get("params", {})):
            return pending_response
        return update_response

    mock_requests.get.side_effect = route_requests
    mock_requests.patch.return_value = update_response
    mock_requests.post.return_value = create_response

    from tasks.generate_content import run
    run()

    assert mock_requests.post.call_count >= 3
```

- [ ] **Step 2: Run smoke test**

Run: `cd orchestrator && python -m pytest tests/test_smoke.py -v`
Expected: PASS.

- [ ] **Step 3: Run full test suite**

Run: `cd orchestrator && python -m pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add orchestrator/tests/test_smoke.py
git commit -m "test(orchestrator): end-to-end smoke test for content generation"
```

---

## Summary

| Task | Component | Agents Involved |
|------|-----------|-----------------|
| 1 | Config + deps | — |
| 2 | LLM Router | — |
| 3 | Agent base class | — |
| 4 | Concrete agents | researcher, content_planner, copywriter, video_scripter, reporter |
| 5 | Content workflow | researcher → planner → scripter |
| 6 | Outreach workflow | researcher → copywriter |
| 7 | Report workflow | reporter |
| 8 | Rewire tasks | — |
| 9 | Social post agent | social_poster (added to content workflow) |
| 10 | Smoke test | full stack validation |
