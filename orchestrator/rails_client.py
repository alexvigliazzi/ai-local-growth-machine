import requests
from config import RAILS_API_URL, API_TOKEN


class RailsClient:
    def __init__(self):
        self.base_url = RAILS_API_URL
        self.headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(self, path, params=None):
        resp = requests.get(f"{self.base_url}{path}", headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path, data):
        resp = requests.post(f"{self.base_url}{path}", headers=self.headers, json=data)
        resp.raise_for_status()
        return resp.json()

    def _patch(self, path, data):
        resp = requests.patch(f"{self.base_url}{path}", headers=self.headers, json=data)
        resp.raise_for_status()
        return resp.json()

    # Content Requests
    def get_pending_content_requests(self):
        return self._get("/content_requests", params={"status": "pending"})

    def mark_content_request_in_progress(self, request_id):
        return self._patch(f"/content_requests/{request_id}", {"status": "in_progress"})

    def mark_content_request_completed(self, request_id):
        return self._patch(f"/content_requests/{request_id}", {"status": "completed"})

    # Content Outputs
    def create_content_output(self, content_request_id, title, content, output_type):
        return self._post("/content_outputs", {
            "content_output": {
                "content_request_id": content_request_id,
                "title": title,
                "content": content,
                "output_type": output_type,
                "status": "draft",
            }
        })

    # Leads
    def get_leads(self, status=None):
        params = {"status": status} if status else None
        return self._get("/leads", params=params)

    def get_lead(self, lead_id):
        return self._get(f"/leads/{lead_id}")

    # Outreach Messages
    def create_outreach_message(self, lead_id, channel, message, message_type):
        return self._post("/outreach_messages", {
            "outreach_message": {
                "lead_id": lead_id,
                "channel": channel,
                "message": message,
                "message_type": message_type,
                "status": "pending",
            }
        })

    def get_queued_outreach_messages(self):
        return self._get("/outreach_messages", params={"status": "queued"})

    def fill_outreach_message(self, message_id, message_text):
        return self._patch(f"/outreach_messages/{message_id}", {
            "outreach_message": {"message": message_text, "status": "pending"}
        })

    # Clients
    def get_clients(self, status=None):
        params = {"status": status} if status else None
        return self._get("/clients", params=params)

    def get_client_with_summary(self, client_id):
        return self._get(f"/clients/{client_id}")

    # Reports
    def create_report(self, client_id, title, content):
        return self._post("/reports", {
            "report": {
                "client_id": client_id,
                "title": title,
                "content": content,
            }
        })
