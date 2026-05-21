import os

RAILS_API_URL = os.environ.get("RAILS_API_URL", "http://localhost:3000/api")
API_TOKEN = os.environ.get("API_TOKEN", "")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:1b-it-qat")

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "automations", "prompts")
