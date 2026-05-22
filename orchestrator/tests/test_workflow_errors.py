"""Unit 5: Workflow error propagation — mid-pipeline failures."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

CLIENT = {"business_name": "Cafe Central", "niche": "cafeteria", "city": "Campinas", "plan": "starter"}
REQUEST = {"objective": "engajamento", "services": "cafe, bolo", "tone": "informal", "references": ""}
LEAD = {"business_name": "Biz", "niche": "motos", "city": "BH", "instagram_url": "", "notes": ""}


# --- Content Generation Workflow ---


class TestContentGenerationErrors:
    @patch("workflows.content_generation.SocialPosterAgent")
    @patch("workflows.content_generation.VideoScripterAgent")
    @patch("workflows.content_generation.ContentPlannerAgent")
    @patch("workflows.content_generation.ResearcherAgent")
    def test_researcher_fails_entire_pipeline_fails(
        self, mock_researcher_cls, mock_planner_cls, mock_scripter_cls, mock_poster_cls
    ):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher
        mock_researcher.research.side_effect = RuntimeError("LLM failed")

        from workflows.content_generation import ContentGenerationWorkflow

        with pytest.raises(RuntimeError, match="LLM failed"):
            ContentGenerationWorkflow().run(client=CLIENT, request=REQUEST)

        mock_planner_cls.assert_not_called()

    @patch("workflows.content_generation.SocialPosterAgent")
    @patch("workflows.content_generation.VideoScripterAgent")
    @patch("workflows.content_generation.ContentPlannerAgent")
    @patch("workflows.content_generation.ResearcherAgent")
    def test_planner_fails_after_research_succeeds(
        self, mock_researcher_cls, mock_planner_cls, mock_scripter_cls, mock_poster_cls
    ):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher
        mock_researcher.research.return_value = "research ok"

        mock_planner = MagicMock()
        mock_planner_cls.return_value = mock_planner
        mock_planner.plan.side_effect = RuntimeError("Planner LLM down")

        from workflows.content_generation import ContentGenerationWorkflow

        with pytest.raises(RuntimeError, match="Planner LLM down"):
            ContentGenerationWorkflow().run(client=CLIENT, request=REQUEST)

    @patch("workflows.content_generation.SocialPosterAgent")
    @patch("workflows.content_generation.VideoScripterAgent")
    @patch("workflows.content_generation.ContentPlannerAgent")
    @patch("workflows.content_generation.ResearcherAgent")
    def test_social_poster_fails_after_planner(
        self, mock_researcher_cls, mock_planner_cls, mock_scripter_cls, mock_poster_cls
    ):
        """COVERAGE GAP: SocialPosterAgent was not mocked in existing tests."""
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher
        mock_researcher.research.return_value = "research ok"

        mock_planner = MagicMock()
        mock_planner_cls.return_value = mock_planner
        mock_planner.plan.return_value = "plan ok"

        mock_poster = MagicMock()
        mock_poster_cls.return_value = mock_poster
        mock_poster.post.side_effect = RuntimeError("Poster LLM down")

        from workflows.content_generation import ContentGenerationWorkflow

        with pytest.raises(RuntimeError, match="Poster LLM down"):
            ContentGenerationWorkflow().run(client=CLIENT, request=REQUEST)

    @patch("workflows.content_generation.SocialPosterAgent")
    @patch("workflows.content_generation.VideoScripterAgent")
    @patch("workflows.content_generation.ContentPlannerAgent")
    @patch("workflows.content_generation.ResearcherAgent")
    def test_video_scripter_fails_after_poster(
        self, mock_researcher_cls, mock_planner_cls, mock_scripter_cls, mock_poster_cls
    ):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher
        mock_researcher.research.return_value = "research ok"

        mock_planner = MagicMock()
        mock_planner_cls.return_value = mock_planner
        mock_planner.plan.return_value = "plan ok"

        mock_poster = MagicMock()
        mock_poster_cls.return_value = mock_poster
        mock_poster.post.return_value = "post ok"

        mock_scripter = MagicMock()
        mock_scripter_cls.return_value = mock_scripter
        mock_scripter.script.side_effect = RuntimeError("Scripter failed")

        from workflows.content_generation import ContentGenerationWorkflow

        with pytest.raises(RuntimeError, match="Scripter failed"):
            ContentGenerationWorkflow().run(client=CLIENT, request=REQUEST)


# --- Lead Outreach Workflow ---


class TestLeadOutreachErrors:
    @patch("workflows.lead_outreach.CopywriterAgent")
    @patch("workflows.lead_outreach.ResearcherAgent")
    def test_researcher_fails_copywriter_never_called(self, mock_researcher_cls, mock_copywriter_cls):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher
        mock_researcher.research.side_effect = RuntimeError("Research failed")

        from workflows.lead_outreach import LeadOutreachWorkflow

        with pytest.raises(RuntimeError):
            LeadOutreachWorkflow().run(lead=LEAD, channel="whatsapp", message_type="primeiro_contato")

        mock_copywriter_cls.assert_not_called()

    @patch("workflows.lead_outreach.CopywriterAgent")
    @patch("workflows.lead_outreach.ResearcherAgent")
    def test_copywriter_fails_after_research(self, mock_researcher_cls, mock_copywriter_cls):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher
        mock_researcher.research.return_value = "research ok"

        mock_copywriter = MagicMock()
        mock_copywriter_cls.return_value = mock_copywriter
        mock_copywriter.write.side_effect = RuntimeError("Copywriter down")

        from workflows.lead_outreach import LeadOutreachWorkflow

        with pytest.raises(RuntimeError, match="Copywriter down"):
            LeadOutreachWorkflow().run(lead=LEAD, channel="whatsapp", message_type="primeiro_contato")


# --- Weekly Report Workflow ---


class TestWeeklyReportErrors:
    @patch("workflows.weekly_report.ReporterAgent")
    def test_reporter_fails(self, mock_reporter_cls):
        mock_reporter = MagicMock()
        mock_reporter_cls.return_value = mock_reporter
        mock_reporter.report.side_effect = RuntimeError("Reporter crashed")

        from workflows.weekly_report import WeeklyReportWorkflow

        with pytest.raises(RuntimeError, match="Reporter crashed"):
            WeeklyReportWorkflow().run(
                client=CLIENT,
                period_start="14/05/2026",
                period_end="21/05/2026",
                outputs_summary="- Post (social_post) — approved",
            )


# --- Missing data ---


class TestMissingData:
    @patch("workflows.content_generation.SocialPosterAgent")
    @patch("workflows.content_generation.VideoScripterAgent")
    @patch("workflows.content_generation.ContentPlannerAgent")
    @patch("workflows.content_generation.ResearcherAgent")
    def test_content_workflow_missing_business_name(
        self, mock_researcher_cls, mock_planner_cls, mock_scripter_cls, mock_poster_cls
    ):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher

        from workflows.content_generation import ContentGenerationWorkflow

        bad_client = {"niche": "cafe", "city": "SP"}  # missing business_name
        with pytest.raises(KeyError):
            ContentGenerationWorkflow().run(client=bad_client, request=REQUEST)

    @patch("workflows.lead_outreach.CopywriterAgent")
    @patch("workflows.lead_outreach.ResearcherAgent")
    def test_outreach_missing_lead_niche(self, mock_researcher_cls, mock_copywriter_cls):
        mock_researcher = MagicMock()
        mock_researcher_cls.return_value = mock_researcher

        from workflows.lead_outreach import LeadOutreachWorkflow

        bad_lead = {"business_name": "Biz", "city": "BH"}  # missing niche
        with pytest.raises(KeyError):
            LeadOutreachWorkflow().run(lead=bad_lead, channel="whatsapp", message_type="primeiro_contato")
