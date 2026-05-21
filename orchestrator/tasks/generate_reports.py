"""Generate weekly reports for active clients via Ollama, post back to Rails."""

import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rails_client import RailsClient
from ai_client import AiClient
from prompt_renderer import PromptRenderer


def run():
    rails = RailsClient()
    ai = AiClient()
    renderer = PromptRenderer()

    clients = rails.get_clients(status="active")
    if not clients:
        print("No active clients.")
        return

    today = datetime.now()
    week_ago = today - timedelta(days=7)

    for client in clients:
        print(f"Generating report for: {client['business_name']}")

        details = rails.get_client_with_summary(client["id"])
        weekly_outputs = details.get("weekly_outputs", [])

        if not weekly_outputs:
            print(f"  No outputs this week, skipping.")
            continue

        outputs_summary = "\n".join(
            f"- {o['title']} ({o['output_type']}) — {o['status']}"
            for o in weekly_outputs
        )

        variables = {
            "business_name": client["business_name"],
            "niche": client["niche"],
            "plan": client.get("plan") or "starter",
            "period_start": week_ago.strftime("%d/%m/%Y"),
            "period_end": today.strftime("%d/%m/%Y"),
            "content_outputs_summary": outputs_summary,
            "metrics": "Sem metricas disponiveis neste periodo.",
        }

        try:
            system_prompt, user_prompt = renderer.render("weekly_report", variables)
            content = ai.generate(system_prompt, user_prompt)

            title = f"Relatorio Semanal — {client['business_name']} — {today.strftime('%d/%m/%Y')}"
            result = rails.create_report(client["id"], title, content)
            print(f"  Created report (token: {result['token']})")
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    run()
