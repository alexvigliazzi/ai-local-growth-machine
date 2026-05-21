"""CLI entry point for the orchestrator.

Usage:
    python run.py content     # generate content for pending requests
    python run.py outreach    # generate outreach messages for new leads
    python run.py reports     # generate weekly reports for active clients
    python run.py all         # run all tasks
"""

import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    task = sys.argv[1]

    if task in ("content", "all"):
        from tasks.generate_content import run as run_content
        print("=== Content Generation ===")
        run_content()

    if task in ("outreach", "all"):
        from tasks.generate_outreach import run as run_outreach
        print("=== Outreach Messages ===")
        run_outreach()

    if task in ("reports", "all"):
        from tasks.generate_reports import run as run_reports
        print("=== Weekly Reports ===")
        run_reports()

    if task not in ("content", "outreach", "reports", "all"):
        print(f"Unknown task: {task}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
