from agents.reporter import ReporterAgent


class WeeklyReportWorkflow:
    def run(self, client: dict, period_start: str, period_end: str,
            outputs_summary: str, metrics: str = "") -> dict:
        print(f"  [1/1] Generating report for: {client['business_name']}...")
        reporter = ReporterAgent()
        report = reporter.report(
            client=client,
            period_start=period_start,
            period_end=period_end,
            outputs_summary=outputs_summary,
            metrics=metrics,
        )
        return {"report": report}
