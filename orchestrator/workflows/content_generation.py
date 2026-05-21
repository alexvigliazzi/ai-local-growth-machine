from agents.researcher import ResearcherAgent
from agents.content_planner import ContentPlannerAgent
from agents.video_scripter import VideoScripterAgent


class ContentGenerationWorkflow:
    def run(self, client: dict, request: dict) -> dict:
        results = {}

        print(f"  [1/3] Researching: {client['business_name']}...")
        researcher = ResearcherAgent()
        results["research"] = researcher.research(
            business_name=client["business_name"],
            niche=client["niche"],
            city=client["city"],
            services=request.get("services") or "",
        )

        print(f"  [2/3] Planning content...")
        planner = ContentPlannerAgent()
        results["content_plan"] = planner.plan(
            client=client,
            request=request,
            research_context=results["research"],
        )

        print(f"  [3/3] Writing video scripts...")
        scripter = VideoScripterAgent()
        results["video_script"] = scripter.script(
            client=client,
            request=request,
            themes=request.get("objective") or "",
        )

        return results
