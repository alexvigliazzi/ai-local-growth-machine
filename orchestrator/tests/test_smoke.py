"""Smoke test: validates generate_content task with fully mocked Rails + LLM."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@patch("ai_client.anthropic.Anthropic")
@patch("ai_client.ollama.Client")
@patch("rails_client.requests")
def test_generate_content_end_to_end(mock_requests, mock_ollama_cls, mock_anthropic_cls):
    mock_ollama = MagicMock()
    mock_ollama_cls.return_value = mock_ollama
    mock_ollama.chat.return_value = {"message": {"content": "ollama output"}}

    mock_anthropic = MagicMock()
    mock_anthropic_cls.return_value = mock_anthropic
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="claude output")]
    mock_anthropic.messages.create.return_value = mock_response

    pending_response = MagicMock()
    pending_response.json.return_value = [{
        "id": "req-1",
        "objective": "engajamento",
        "services": "cafe, bolo",
        "tone": "informal",
        "references": "",
        "client": {
            "id": "cli-1",
            "business_name": "Cafe Central",
            "niche": "cafeteria",
            "city": "Campinas",
            "plan": "starter",
        },
    }]
    pending_response.raise_for_status = MagicMock()

    update_response = MagicMock()
    update_response.json.return_value = {"id": "req-1", "status": "in_progress"}
    update_response.raise_for_status = MagicMock()

    create_response = MagicMock()
    create_response.json.return_value = {"id": "out-1", "status": "draft"}
    create_response.raise_for_status = MagicMock()
    create_response.status_code = 201

    def route_requests(url, **kwargs):
        params = kwargs.get("params") or {}
        if params.get("status") == "pending":
            return pending_response
        return update_response

    mock_requests.get.side_effect = route_requests
    mock_requests.patch.return_value = update_response
    mock_requests.post.return_value = create_response

    from tasks.generate_content import run
    run()

    assert mock_requests.post.call_count >= 3
