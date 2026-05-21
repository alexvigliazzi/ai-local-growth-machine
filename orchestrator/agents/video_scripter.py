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
