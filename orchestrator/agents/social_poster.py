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
