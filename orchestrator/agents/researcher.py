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
