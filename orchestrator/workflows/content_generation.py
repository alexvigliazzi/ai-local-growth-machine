from agents.researcher import ResearcherAgent
from agents.content_planner import ContentPlannerAgent
from agents.video_scripter import VideoScripterAgent
from agents.social_poster import SocialPosterAgent


class ContentGenerationWorkflow:
    def run(self, client: dict, request: dict) -> dict:
        results = {}

        print(f"  [1/4] Researching: {client['business_name']}...")
        researcher = ResearcherAgent()
        results["research"] = researcher.research(
            business_name=client["business_name"],
            niche=client["niche"],
            city=client["city"],
            services=request.get("services") or "",
        )

        print(f"  [2/4] Planning content...")
        planner = ContentPlannerAgent()
        results["content_plan"] = planner.plan(
            client=client,
            request=request,
            research_context=results["research"],
        )

        print(f"  [3/4] Writing social posts...")
        poster = SocialPosterAgent()
        results["social_post"] = poster.post(
            client=client,
            request=request,
            themes=request.get("objective") or "",
        )

        print(f"  [4/4] Writing video scripts...")
        scripter = VideoScripterAgent()
        results["video_script"] = scripter.script(
            client=client,
            request=request,
            themes=request.get("objective") or "",
        )

        return results
