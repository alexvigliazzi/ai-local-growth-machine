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
