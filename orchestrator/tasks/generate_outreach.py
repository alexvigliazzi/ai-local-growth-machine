"""Generate outreach messages.

Two modes:
  - queued: fills messages explicitly queued from the admin UI (status=queued)
  - new:    generates a first-contact message for every lead with status=new
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rails_client import RailsClient
from ai_client import AiClient
from prompt_renderer import PromptRenderer


def run():
    rails = RailsClient()
    ai = AiClient()
    renderer = PromptRenderer()

    processed = 0

    # Priority: fill explicitly queued messages (created from admin UI)
    queued = rails.get_queued_outreach_messages()
    for msg in queued:
        lead = rails.get_lead(msg["lead_id"])
        print(f"Filling queued message: {lead['business_name']} via {msg['channel']}")

        variables = {
            "business_name": lead["business_name"],
            "niche": lead["niche"],
            "city": lead["city"],
            "channel": msg["channel"],
            "instagram_url": lead.get("instagram_url") or "",
            "notes": lead.get("notes") or "",
            "message_type": msg["message_type"],
        }

        try:
            system_prompt, user_prompt = renderer.render("outreach_message", variables)
            content = ai.generate(system_prompt, user_prompt)
            rails.fill_outreach_message(msg["id"], content)
            print(f"  Done: {lead['business_name']}")
            processed += 1
        except Exception as e:
            print(f"  Error: {e}")

    if not queued:
        print("No queued messages from admin UI.")

    print(f"\nProcessed {processed} message(s).")


if __name__ == "__main__":
    run()
