"""Unit 6: Task runner integration — generate_content, generate_outreach, generate_reports."""

import pytest
from unittest.mock import patch, MagicMock, call
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


PENDING_REQ = {
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
}

QUEUED_MSG = {
    "id": "msg-1",
    "lead_id": "lead-1",
    "channel": "whatsapp",
    "message_type": "primeiro_contato",
}

LEAD = {
    "id": "lead-1",
    "business_name": "Moto Shop",
    "niche": "motos",
    "city": "BH",
    "instagram_url": "https://instagram.com/motoshop",
    "notes": "Interessado",
}

ACTIVE_CLIENT = {
    "id": "cli-1",
    "business_name": "Cafe Central",
    "niche": "cafeteria",
    "city": "Campinas",
    "plan": "starter",
}


# === generate_content ===


class TestGenerateContent:
    @patch("tasks.generate_content.ContentGenerationWorkflow")
    @patch("tasks.generate_content.RailsClient")
    def test_empty_pending_does_nothing(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_pending_content_requests.return_value = []

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf

        from tasks.generate_content import run
        run()

        mock_wf.run.assert_not_called()

    @patch("tasks.generate_content.ContentGenerationWorkflow")
    @patch("tasks.generate_content.RailsClient")
    def test_marks_in_progress_before_workflow(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_pending_content_requests.return_value = [PENDING_REQ]

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.return_value = {"research": "r", "content_plan": "cp", "social_post": "sp", "video_script": "vs"}

        from tasks.generate_content import run
        run()

        mock_rails.mark_content_request_in_progress.assert_called_once_with("req-1")

    @patch("tasks.generate_content.ContentGenerationWorkflow")
    @patch("tasks.generate_content.RailsClient")
    def test_creates_three_outputs_on_success(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_pending_content_requests.return_value = [PENDING_REQ]

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.return_value = {"research": "r", "content_plan": "cp", "social_post": "sp", "video_script": "vs"}

        from tasks.generate_content import run
        run()

        assert mock_rails.create_content_output.call_count == 3
        output_types = [c.args[3] for c in mock_rails.create_content_output.call_args_list]
        assert "content_plan" in output_types
        assert "social_post" in output_types
        assert "video_script" in output_types

    @patch("tasks.generate_content.ContentGenerationWorkflow")
    @patch("tasks.generate_content.RailsClient")
    def test_marks_completed_after_outputs(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_pending_content_requests.return_value = [PENDING_REQ]

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.return_value = {"research": "r", "content_plan": "cp", "social_post": "sp", "video_script": "vs"}

        from tasks.generate_content import run
        run()

        mock_rails.mark_content_request_completed.assert_called_once_with("req-1")

    @patch("tasks.generate_content.ContentGenerationWorkflow")
    @patch("tasks.generate_content.RailsClient")
    def test_workflow_error_does_not_mark_completed(self, mock_rails_cls, mock_workflow_cls):
        """BUG DOCUMENTATION: request stays in 'in_progress' forever when workflow fails."""
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_pending_content_requests.return_value = [PENDING_REQ]

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.side_effect = RuntimeError("LLM down")

        from tasks.generate_content import run
        run()  # should not raise (task catches errors)

        mock_rails.mark_content_request_in_progress.assert_called_once()
        mock_rails.mark_content_request_completed.assert_not_called()  # BUG: stuck in in_progress

    @patch("tasks.generate_content.ContentGenerationWorkflow")
    @patch("tasks.generate_content.RailsClient")
    def test_continues_to_next_request_after_error(self, mock_rails_cls, mock_workflow_cls):
        req2 = dict(PENDING_REQ, id="req-2")
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_pending_content_requests.return_value = [PENDING_REQ, req2]

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.side_effect = [
            RuntimeError("First fails"),
            {"research": "r", "content_plan": "cp", "social_post": "sp", "video_script": "vs"},
        ]

        from tasks.generate_content import run
        run()

        assert mock_rails.mark_content_request_in_progress.call_count == 2
        mock_rails.mark_content_request_completed.assert_called_once_with("req-2")

    @patch("tasks.generate_content.ContentGenerationWorkflow")
    @patch("tasks.generate_content.RailsClient")
    def test_skips_missing_output_type(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_pending_content_requests.return_value = [PENDING_REQ]

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.return_value = {"research": "r", "content_plan": "cp"}  # no social_post or video_script

        from tasks.generate_content import run
        run()

        assert mock_rails.create_content_output.call_count == 1


# === generate_outreach ===


class TestGenerateOutreach:
    @patch("tasks.generate_outreach.LeadOutreachWorkflow")
    @patch("tasks.generate_outreach.RailsClient")
    def test_empty_queue_does_nothing(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_queued_outreach_messages.return_value = []

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf

        from tasks.generate_outreach import run
        run()

        mock_wf.run.assert_not_called()

    @patch("tasks.generate_outreach.LeadOutreachWorkflow")
    @patch("tasks.generate_outreach.RailsClient")
    def test_processes_each_message(self, mock_rails_cls, mock_workflow_cls):
        msg2 = dict(QUEUED_MSG, id="msg-2", lead_id="lead-2")
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_queued_outreach_messages.return_value = [QUEUED_MSG, msg2]
        mock_rails.get_lead.return_value = LEAD

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.return_value = {"research": "r", "message": "Oi!"}

        from tasks.generate_outreach import run
        run()

        assert mock_rails.fill_outreach_message.call_count == 2

    @patch("tasks.generate_outreach.LeadOutreachWorkflow")
    @patch("tasks.generate_outreach.RailsClient")
    def test_single_error_continues(self, mock_rails_cls, mock_workflow_cls):
        msg2 = dict(QUEUED_MSG, id="msg-2", lead_id="lead-2")
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_queued_outreach_messages.return_value = [QUEUED_MSG, msg2]
        mock_rails.get_lead.return_value = LEAD

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.side_effect = [RuntimeError("first fails"), {"research": "r", "message": "ok"}]

        from tasks.generate_outreach import run
        run()

        assert mock_rails.fill_outreach_message.call_count == 1

    @patch("tasks.generate_outreach.LeadOutreachWorkflow")
    @patch("tasks.generate_outreach.RailsClient")
    def test_get_lead_called_with_correct_id(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_queued_outreach_messages.return_value = [QUEUED_MSG]
        mock_rails.get_lead.return_value = LEAD

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.return_value = {"research": "r", "message": "msg"}

        from tasks.generate_outreach import run
        run()

        mock_rails.get_lead.assert_called_once_with("lead-1")


# === generate_reports ===


class TestGenerateReports:
    @patch("tasks.generate_reports.WeeklyReportWorkflow")
    @patch("tasks.generate_reports.RailsClient")
    def test_no_active_clients_does_nothing(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_clients.return_value = []

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf

        from tasks.generate_reports import run
        run()

        mock_wf.run.assert_not_called()

    @patch("tasks.generate_reports.WeeklyReportWorkflow")
    @patch("tasks.generate_reports.RailsClient")
    def test_skips_client_without_weekly_outputs(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_clients.return_value = [ACTIVE_CLIENT]
        mock_rails.get_client_with_summary.return_value = {"weekly_outputs": []}

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf

        from tasks.generate_reports import run
        run()

        mock_wf.run.assert_not_called()

    @patch("tasks.generate_reports.WeeklyReportWorkflow")
    @patch("tasks.generate_reports.RailsClient")
    def test_creates_report_on_success(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_clients.return_value = [ACTIVE_CLIENT]
        mock_rails.get_client_with_summary.return_value = {
            "weekly_outputs": [{"title": "Post", "output_type": "social_post", "status": "approved"}]
        }
        mock_rails.create_report.return_value = {"id": "rpt-1", "token": "abc123"}

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.return_value = {"report": "Weekly report content"}

        from tasks.generate_reports import run
        run()

        mock_rails.create_report.assert_called_once()
        call_args = mock_rails.create_report.call_args[0]
        assert call_args[0] == "cli-1"  # client_id
        assert "Cafe Central" in call_args[1]  # title contains business name
        assert call_args[2] == "Weekly report content"  # content

    @patch("tasks.generate_reports.WeeklyReportWorkflow")
    @patch("tasks.generate_reports.RailsClient")
    def test_error_continues_to_next_client(self, mock_rails_cls, mock_workflow_cls):
        client2 = dict(ACTIVE_CLIENT, id="cli-2", business_name="Padaria Boa")
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_clients.return_value = [ACTIVE_CLIENT, client2]
        mock_rails.get_client_with_summary.return_value = {
            "weekly_outputs": [{"title": "Post", "output_type": "social_post", "status": "approved"}]
        }
        mock_rails.create_report.return_value = {"id": "rpt-1", "token": "tok"}

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.side_effect = [RuntimeError("first fails"), {"report": "ok"}]

        from tasks.generate_reports import run
        run()

        assert mock_rails.create_report.call_count == 1

    @patch("tasks.generate_reports.WeeklyReportWorkflow")
    @patch("tasks.generate_reports.RailsClient")
    def test_report_title_format(self, mock_rails_cls, mock_workflow_cls):
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_clients.return_value = [ACTIVE_CLIENT]
        mock_rails.get_client_with_summary.return_value = {
            "weekly_outputs": [{"title": "Post", "output_type": "social_post", "status": "approved"}]
        }
        mock_rails.create_report.return_value = {"id": "rpt-1", "token": "tok"}

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.return_value = {"report": "content"}

        from tasks.generate_reports import run
        run()

        title = mock_rails.create_report.call_args[0][1]
        assert "Relatorio Semanal" in title
        assert "Cafe Central" in title

    @patch("tasks.generate_reports.WeeklyReportWorkflow")
    @patch("tasks.generate_reports.RailsClient")
    def test_accesses_result_token(self, mock_rails_cls, mock_workflow_cls):
        """BUG DOCUMENTATION: generate_reports accesses result['token'].

        If Rails omits 'token' from the response, generate_reports catches the
        KeyError in its generic except block — the error is logged but the client
        is silently skipped. This documents the fragile dependency.
        """
        mock_rails = MagicMock()
        mock_rails_cls.return_value = mock_rails
        mock_rails.get_clients.return_value = [ACTIVE_CLIENT]
        mock_rails.get_client_with_summary.return_value = {
            "weekly_outputs": [{"title": "Post", "output_type": "social_post", "status": "approved"}]
        }
        # Return response WITHOUT 'token' field
        mock_rails.create_report.return_value = {"id": "rpt-1"}

        mock_wf = MagicMock()
        mock_workflow_cls.return_value = mock_wf
        mock_wf.run.return_value = {"report": "content"}

        from tasks.generate_reports import run

        # Doesn't raise — the KeyError is caught by the generic except.
        # But the report is silently treated as failed.
        run()  # should not raise

        # Report was created (Rails call succeeded) but error was logged
        mock_rails.create_report.assert_called_once()
