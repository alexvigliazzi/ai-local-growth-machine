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


# Backward-compatible alias — model/host params kept for signature compat but ignored.
# New code should use LLMRouter(profile=...) directly.
class AiClient:
    def __init__(self, model=None, host=None):
        if model or host:
            print(f"[AiClient] Warning: model/host params are deprecated and ignored. Use LLMRouter.")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        router = LLMRouter(profile="fast")
        return router.generate(system_prompt, user_prompt)
