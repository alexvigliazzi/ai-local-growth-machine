"""Generate weekly reports using the weekly report workflow."""

import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rails_client import RailsClient
from workflows.weekly_report import WeeklyReportWorkflow


def run():
    rails = RailsClient()
    workflow = WeeklyReportWorkflow()

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

        try:
            results = workflow.run(
                client=client,
                period_start=week_ago.strftime("%d/%m/%Y"),
                period_end=today.strftime("%d/%m/%Y"),
                outputs_summary=outputs_summary,
            )

            title = f"Relatorio Semanal — {client['business_name']} — {today.strftime('%d/%m/%Y')}"
            result = rails.create_report(client["id"], title, results["report"])
            print(f"  Created report (id: {result.get('id', 'N/A')}, token: {result.get('token', 'N/A')})")
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    run()
