import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestContentGenerationWorkflow:
    @patch("workflows.content_generation.SocialPosterAgent")
    @patch("workflows.content_generation.VideoScripterAgent")
    @patch("workflows.content_generation.ContentPlannerAgent")
    @patch("workflows.content_generation.ResearcherAgent")
    def test_pipeline_runs_all_agents(self, mock_researcher_cls, mock_planner_cls, mock_scripter_cls, mock_poster_cls):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher
        mock_researcher.research.return_value = "research output"

        mock_planner = MagicMock()
        mock_planner_cls.return_value = mock_planner
        mock_planner.plan.return_value = "content plan output"

        mock_poster = MagicMock()
        mock_poster_cls.return_value = mock_poster
        mock_poster.post.return_value = "social post output"

        mock_scripter = MagicMock()
        mock_scripter_cls.return_value = mock_scripter
        mock_scripter.script.return_value = "video script output"

        from workflows.content_generation import ContentGenerationWorkflow

        client = {"business_name": "Test", "niche": "cafe", "city": "SP"}
        request = {"objective": "engajamento", "services": "cafe", "tone": "informal", "references": ""}

        workflow = ContentGenerationWorkflow()
        results = workflow.run(client=client, request=request)

        mock_researcher.research.assert_called_once()
        mock_planner.plan.assert_called_once()
        mock_poster.post.assert_called_once()
        mock_scripter.script.assert_called_once()

        assert results["research"] == "research output"
        assert results["content_plan"] == "content plan output"
        assert results["social_post"] == "social post output"
        assert results["video_script"] == "video script output"


class TestLeadOutreachWorkflow:
    @patch("workflows.lead_outreach.CopywriterAgent")
    @patch("workflows.lead_outreach.ResearcherAgent")
    def test_pipeline_runs_researcher_then_copywriter(self, mock_researcher_cls, mock_copywriter_cls):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher
        mock_researcher.research.return_value = "lead research"

        mock_copywriter = MagicMock()
        mock_copywriter_cls.return_value = mock_copywriter
        mock_copywriter.write.return_value = "outreach message"

        from workflows.lead_outreach import LeadOutreachWorkflow

        lead = {"business_name": "Biz", "niche": "motos", "city": "BH",
                "instagram_url": "", "notes": ""}

        workflow = LeadOutreachWorkflow()
        result = workflow.run(lead=lead, channel="whatsapp", message_type="primeiro_contato")

        mock_researcher.research.assert_called_once()
        mock_copywriter.write.assert_called_once()
        assert result["message"] == "outreach message"


class TestWeeklyReportWorkflow:
    @patch("workflows.weekly_report.ReporterAgent")
    def test_pipeline_runs_reporter(self, mock_reporter_cls):
        mock_reporter = MagicMock()
        mock_reporter_cls.return_value = mock_reporter
        mock_reporter.report.return_value = "report content"

        from workflows.weekly_report import WeeklyReportWorkflow

        client = {"business_name": "Biz", "niche": "cafe", "plan": "starter"}

        workflow = WeeklyReportWorkflow()
        result = workflow.run(
            client=client,
            period_start="14/05/2026",
            period_end="21/05/2026",
            outputs_summary="- Post 1 (social_post) — approved",
        )

        mock_reporter.report.assert_called_once()
        assert result["report"] == "report content"
