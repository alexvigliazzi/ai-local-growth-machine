from agents.researcher import ResearcherAgent
from agents.copywriter import CopywriterAgent


class LeadOutreachWorkflow:
    def run(self, lead: dict, channel: str, message_type: str) -> dict:
        results = {}

        print(f"  [1/2] Researching lead: {lead['business_name']}...")
        researcher = ResearcherAgent()
        results["research"] = researcher.research(
            business_name=lead["business_name"],
            niche=lead["niche"],
            city=lead["city"],
            instagram_url=lead.get("instagram_url") or "",
        )

        print(f"  [2/2] Writing {message_type} for {channel}...")
        copywriter = CopywriterAgent()
        results["message"] = copywriter.write(
            lead=lead,
            channel=channel,
            message_type=message_type,
            research_context=results["research"],
        )

        return results
