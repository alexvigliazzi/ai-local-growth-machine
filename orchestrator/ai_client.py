import ollama
from config import OLLAMA_HOST, OLLAMA_MODEL


class AiClient:
    def __init__(self, model=None, host=None):
        self.model = model or OLLAMA_MODEL
        self.client = ollama.Client(host=host or OLLAMA_HOST)

    def generate(self, system_prompt, user_prompt):
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response["message"]["content"]
