"""Weekly scheduler for the Growth Machine orchestrator.

Runs as a long-lived process. Executes report generation every Sunday at 09:00.
Also supports outreach processing every Monday at 08:00.

Usage:
    python scheduler.py

Environment:
    RAILS_API_URL   — defaults to http://localhost:3000/api
    API_TOKEN       — required
    OLLAMA_MODEL    — defaults to gemma3:1b-it-qat
    SCHEDULER_LOG   — log file path (optional, defaults to stdout + scheduler.log)
"""

import os
import sys
import time
import logging
from datetime import datetime

import schedule

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Logging ──────────────────────────────────────────────────────────────────

log_file = os.environ.get("SCHEDULER_LOG", os.path.join(os.path.dirname(__file__), "scheduler.log"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ── Tasks ─────────────────────────────────────────────────────────────────────

def job_weekly_reports():
    log.info("=== Starting weekly report generation ===")
    try:
        from tasks.generate_reports import run
        run()
        log.info("=== Weekly reports done ===")
    except Exception as e:
        log.error(f"Weekly reports failed: {e}", exc_info=True)


def job_outreach():
    log.info("=== Starting outreach generation ===")
    try:
        from tasks.generate_outreach import run
        run()
        log.info("=== Outreach done ===")
    except Exception as e:
        log.error(f"Outreach generation failed: {e}", exc_info=True)


# ── Schedule ──────────────────────────────────────────────────────────────────

# Weekly reports — every Sunday at 09:00
schedule.every().sunday.at("09:00").do(job_weekly_reports)

# Outreach follow-up — every Monday at 08:00 (process queued messages from the week)
schedule.every().monday.at("08:00").do(job_outreach)


# ── Main loop ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("Scheduler started.")
    log.info(f"  Reports: every Sunday at 09:00")
    log.info(f"  Outreach: every Monday at 08:00")
    log.info(f"  Log: {log_file}")

    next_runs = [(job.next_run, job.job_func.__name__) for job in schedule.jobs]
    for next_run, name in sorted(next_runs):
        log.info(f"  Next '{name}': {next_run.strftime('%Y-%m-%d %H:%M')}")

    while True:
        schedule.run_pending()
        time.sleep(30)
