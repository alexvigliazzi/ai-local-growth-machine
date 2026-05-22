"""Unit 1: RailsClient — HTTP layer and all 12 REST methods."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_response(json_data=None, status_code=200):
    resp = MagicMock()
    resp.json.return_value = json_data or {}
    resp.status_code = status_code
    resp.raise_for_status = MagicMock()
    return resp


# --- HTTP layer ---


@patch("rails_client.requests")
@patch("rails_client.API_TOKEN", "test-tok-123")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_sends_auth_header(mock_requests):
    mock_requests.get.return_value = _make_response([])
    from rails_client import RailsClient

    client = RailsClient()
    client._get("/anything")

    call_kwargs = mock_requests.get.call_args
    headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
    assert headers["Authorization"] == "Bearer test-tok-123"
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_passes_params(mock_requests):
    mock_requests.get.return_value = _make_response([])
    from rails_client import RailsClient

    client = RailsClient()
    client._get("/items", params={"status": "active"})

    call_kwargs = mock_requests.get.call_args
    params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
    assert params == {"status": "active"}


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_post_sends_json_body(mock_requests):
    mock_requests.post.return_value = _make_response({"id": "1"})
    from rails_client import RailsClient

    client = RailsClient()
    client._post("/items", {"name": "test"})

    call_kwargs = mock_requests.post.call_args
    json_arg = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
    assert json_arg == {"name": "test"}


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_patch_sends_json_body(mock_requests):
    mock_requests.patch.return_value = _make_response({"id": "1"})
    from rails_client import RailsClient

    client = RailsClient()
    client._patch("/items/1", {"status": "done"})

    call_kwargs = mock_requests.patch.call_args
    json_arg = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
    assert json_arg == {"status": "done"}


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_raises_on_http_error(mock_requests):
    import requests as real_requests

    resp = MagicMock()
    resp.raise_for_status.side_effect = real_requests.exceptions.HTTPError("500 Server Error")
    mock_requests.get.return_value = resp

    from rails_client import RailsClient

    client = RailsClient()
    with pytest.raises(real_requests.exceptions.HTTPError):
        client._get("/fail")


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_post_raises_on_http_error(mock_requests):
    import requests as real_requests

    resp = MagicMock()
    resp.raise_for_status.side_effect = real_requests.exceptions.HTTPError("422 Unprocessable")
    mock_requests.post.return_value = resp

    from rails_client import RailsClient

    client = RailsClient()
    with pytest.raises(real_requests.exceptions.HTTPError):
        client._post("/fail", {})


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_raises_on_invalid_json(mock_requests):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    mock_requests.get.return_value = resp

    from rails_client import RailsClient

    client = RailsClient()
    with pytest.raises(json.JSONDecodeError):
        client._get("/html-error")


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_raises_on_connection_error(mock_requests):
    import requests as real_requests

    mock_requests.get.side_effect = real_requests.exceptions.ConnectionError("Connection refused")

    from rails_client import RailsClient

    client = RailsClient()
    with pytest.raises(real_requests.exceptions.ConnectionError):
        client._get("/unreachable")


# --- Content Requests ---


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_pending_content_requests_calls_correct_path(mock_requests):
    mock_requests.get.return_value = _make_response([])
    from rails_client import RailsClient

    RailsClient().get_pending_content_requests()

    url = mock_requests.get.call_args[0][0]
    assert url == "http://test:3000/api/content_requests"
    params = mock_requests.get.call_args.kwargs.get("params") or mock_requests.get.call_args[1].get("params")
    assert params == {"status": "pending"}


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_mark_content_request_in_progress(mock_requests):
    mock_requests.patch.return_value = _make_response({"id": "r1", "status": "in_progress"})
    from rails_client import RailsClient

    RailsClient().mark_content_request_in_progress("r1")

    url = mock_requests.patch.call_args[0][0]
    assert "/content_requests/r1" in url
    json_arg = mock_requests.patch.call_args.kwargs.get("json") or mock_requests.patch.call_args[1].get("json")
    assert json_arg == {"status": "in_progress"}


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_mark_content_request_completed(mock_requests):
    mock_requests.patch.return_value = _make_response({"id": "r1", "status": "completed"})
    from rails_client import RailsClient

    RailsClient().mark_content_request_completed("r1")

    json_arg = mock_requests.patch.call_args.kwargs.get("json") or mock_requests.patch.call_args[1].get("json")
    assert json_arg == {"status": "completed"}


# --- Content Outputs ---


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_create_content_output_payload_shape(mock_requests):
    mock_requests.post.return_value = _make_response({"id": "o1"})
    from rails_client import RailsClient

    RailsClient().create_content_output("r1", "My Title", "Body text", "social_post")

    json_arg = mock_requests.post.call_args.kwargs.get("json") or mock_requests.post.call_args[1].get("json")
    assert "content_output" in json_arg
    payload = json_arg["content_output"]
    assert payload["content_request_id"] == "r1"
    assert payload["title"] == "My Title"
    assert payload["content"] == "Body text"
    assert payload["output_type"] == "social_post"
    assert payload["status"] == "draft"


# --- Leads ---


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_leads_without_status(mock_requests):
    mock_requests.get.return_value = _make_response([])
    from rails_client import RailsClient

    RailsClient().get_leads()

    params = mock_requests.get.call_args.kwargs.get("params") or mock_requests.get.call_args[1].get("params")
    assert params is None


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_leads_with_status_filter(mock_requests):
    mock_requests.get.return_value = _make_response([])
    from rails_client import RailsClient

    RailsClient().get_leads(status="new")

    params = mock_requests.get.call_args.kwargs.get("params") or mock_requests.get.call_args[1].get("params")
    assert params == {"status": "new"}


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_lead_single(mock_requests):
    mock_requests.get.return_value = _make_response({"id": "l1"})
    from rails_client import RailsClient

    RailsClient().get_lead("l1")

    url = mock_requests.get.call_args[0][0]
    assert "/leads/l1" in url


# --- Outreach Messages ---


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_create_outreach_message_payload_shape(mock_requests):
    mock_requests.post.return_value = _make_response({"id": "m1"})
    from rails_client import RailsClient

    RailsClient().create_outreach_message("l1", "whatsapp", "Oi!", "primeiro_contato")

    json_arg = mock_requests.post.call_args.kwargs.get("json") or mock_requests.post.call_args[1].get("json")
    assert "outreach_message" in json_arg
    payload = json_arg["outreach_message"]
    assert payload["lead_id"] == "l1"
    assert payload["channel"] == "whatsapp"
    assert payload["message"] == "Oi!"
    assert payload["message_type"] == "primeiro_contato"
    assert payload["status"] == "pending"


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_queued_outreach_messages(mock_requests):
    mock_requests.get.return_value = _make_response([])
    from rails_client import RailsClient

    RailsClient().get_queued_outreach_messages()

    params = mock_requests.get.call_args.kwargs.get("params") or mock_requests.get.call_args[1].get("params")
    assert params == {"status": "queued"}


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_fill_outreach_message_payload_shape(mock_requests):
    mock_requests.patch.return_value = _make_response({"id": "m1"})
    from rails_client import RailsClient

    RailsClient().fill_outreach_message("m1", "Mensagem atualizada")

    url = mock_requests.patch.call_args[0][0]
    assert "/outreach_messages/m1" in url
    json_arg = mock_requests.patch.call_args.kwargs.get("json") or mock_requests.patch.call_args[1].get("json")
    assert json_arg == {"outreach_message": {"message": "Mensagem atualizada", "status": "pending"}}


# --- Clients ---


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_clients_without_status(mock_requests):
    mock_requests.get.return_value = _make_response([])
    from rails_client import RailsClient

    RailsClient().get_clients()

    params = mock_requests.get.call_args.kwargs.get("params") or mock_requests.get.call_args[1].get("params")
    assert params is None


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_clients_with_status(mock_requests):
    mock_requests.get.return_value = _make_response([])
    from rails_client import RailsClient

    RailsClient().get_clients(status="active")

    params = mock_requests.get.call_args.kwargs.get("params") or mock_requests.get.call_args[1].get("params")
    assert params == {"status": "active"}


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_get_client_with_summary(mock_requests):
    mock_requests.get.return_value = _make_response({"id": "c1", "weekly_outputs": []})
    from rails_client import RailsClient

    RailsClient().get_client_with_summary("c1")

    url = mock_requests.get.call_args[0][0]
    assert "/clients/c1" in url


# --- Reports ---


@patch("rails_client.requests")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_create_report_payload_shape(mock_requests):
    mock_requests.post.return_value = _make_response({"id": "rpt1", "token": "abc123"})
    from rails_client import RailsClient

    RailsClient().create_report("c1", "Weekly Report", "Report content here")

    json_arg = mock_requests.post.call_args.kwargs.get("json") or mock_requests.post.call_args[1].get("json")
    assert "report" in json_arg
    payload = json_arg["report"]
    assert payload["client_id"] == "c1"
    assert payload["title"] == "Weekly Report"
    assert payload["content"] == "Report content here"


# --- Edge case: empty token ---


@patch("rails_client.requests")
@patch("rails_client.API_TOKEN", "")
@patch("rails_client.RAILS_API_URL", "http://test:3000/api")
def test_empty_api_token_still_sends_header(mock_requests):
    """BUG DOCUMENTATION: empty API_TOKEN sends 'Bearer ' header to Rails."""
    mock_requests.get.return_value = _make_response([])
    from rails_client import RailsClient

    client = RailsClient()
    assert client.headers["Authorization"] == "Bearer "
