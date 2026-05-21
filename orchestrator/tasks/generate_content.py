"""Fetch pending content requests, generate outputs via Ollama, post back to Rails."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rails_client import RailsClient
from ai_client import AiClient
from prompt_renderer import PromptRenderer

OUTPUT_TYPES = ["content_plan", "social_post", "video_script"]


def run():
    rails = RailsClient()
    ai = AiClient()
    renderer = PromptRenderer()

    pending = rails.get_pending_content_requests()
    if not pending:
        print("No pending content requests.")
        return

    for req in pending:
        client = req["client"]
        print(f"Processing: {client['business_name']} — {req['objective']}")

        rails.mark_content_request_in_progress(req["id"])

        for output_type in OUTPUT_TYPES:
            template_name = output_type
            variables = {
                "business_name": client["business_name"],
                "niche": client["niche"],
                "city": client["city"],
                "services": req["services"] or "",
                "tone": req["tone"] or "profissional",
                "objective": req["objective"] or "",
                "references": req["references"] or "",
                "target_audience": f"Publico local de {client['city']} interessado em {client['niche']}",
                "duration": "7",
                "channel": "instagram",
            }

            try:
                system_prompt, user_prompt = renderer.render(template_name, variables)
                content = ai.generate(system_prompt, user_prompt)

                title = f"{output_type.replace('_', ' ').title()} — {client['business_name']}"
                rails.create_content_output(req["id"], title, content, output_type)
                print(f"  Created: {title}")
            except FileNotFoundError:
                print(f"  Skipped: no template for {output_type}")
            except Exception as e:
                print(f"  Error generating {output_type}: {e}")

        rails.mark_content_request_completed(req["id"])
        print(f"  Completed: {req['id']}")


if __name__ == "__main__":
    run()
