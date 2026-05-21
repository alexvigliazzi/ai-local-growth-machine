"""Generate outreach messages using the lead outreach workflow."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rails_client import RailsClient
from workflows.lead_outreach import LeadOutreachWorkflow


def run():
    rails = RailsClient()
    workflow = LeadOutreachWorkflow()

    processed = 0

    queued = rails.get_queued_outreach_messages()
    for msg in queued:
        lead = rails.get_lead(msg["lead_id"])
        print(f"Processing: {lead['business_name']} via {msg['channel']}")

        try:
            results = workflow.run(
                lead=lead,
                channel=msg["channel"],
                message_type=msg["message_type"],
            )
            rails.fill_outreach_message(msg["id"], results["message"])
            print(f"  Done: {lead['business_name']}")
            processed += 1
        except Exception as e:
            print(f"  Error: {e}")

    if not queued:
        print("No queued messages from admin UI.")

    print(f"\nProcessed {processed} message(s).")


if __name__ == "__main__":
    run()
