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
