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
