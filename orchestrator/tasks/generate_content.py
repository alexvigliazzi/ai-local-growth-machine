"""Fetch pending content requests, run the content generation workflow, post results to Rails."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rails_client import RailsClient
from workflows.content_generation import ContentGenerationWorkflow


def run():
    rails = RailsClient()
    workflow = ContentGenerationWorkflow()

    pending = rails.get_pending_content_requests()
    if not pending:
        print("No pending content requests.")
        return

    for req in pending:
        client = req["client"]
        print(f"Processing: {client['business_name']} — {req['objective']}")

        rails.mark_content_request_in_progress(req["id"])

        try:
            results = workflow.run(client=client, request=req)

            for output_type in ("content_plan", "video_script"):
                if output_type in results:
                    title = f"{output_type.replace('_', ' ').title()} — {client['business_name']}"
                    rails.create_content_output(req["id"], title, results[output_type], output_type)
                    print(f"  Created: {title}")

            rails.mark_content_request_completed(req["id"])
            print(f"  Completed: {req['id']}")
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    run()
