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
