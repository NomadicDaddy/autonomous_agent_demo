"""AIDD-C package entry point."""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

from agent import run_autonomous_agent

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

__all__ = ["DEFAULT_MODEL", "parse_args", "main"]


def parse_args() -> argparse.Namespace:
	"""Parse command line arguments."""
	parser = argparse.ArgumentParser(
		description="Autonomous Coding Agent Demo - Long-running agent harness",
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  # Start fresh project (creates new app from spec)
  python autonomous_agent_demo.py --project-dir ./my_project --spec ./my_spec.txt

  # Onboard existing codebase (analyzes existing code)
  python autonomous_agent_demo.py --project-dir ./existing_app

  # Use a specific model for all phases
  python autonomous_agent_demo.py --project-dir ./my_project --spec ./my_spec.txt --model claude-sonnet-4-5-20250929

  # Use different models for init/onboarding vs coding (cost optimization)
  python autonomous_agent_demo.py --project-dir ./my_project --spec ./my_spec.txt --init-model claude-haiku-4-5-20251001 --code-model claude-sonnet-4-5-20250929

  # Limit iterations for testing
  python autonomous_agent_demo.py --project-dir ./my_project --spec ./my_spec.txt --max-iterations 5

  # Continue existing project
  python autonomous_agent_demo.py --project-dir ./my_project

  # Set idle timeout (abort if no output for N seconds)
  python autonomous_agent_demo.py --project-dir ./my_project --idle-timeout 300

  # Quit after 3 consecutive failures
  python autonomous_agent_demo.py --project-dir ./my_project --quit-on-abort 3

How it works:
  - Empty directory: Uses initializer agent to create new app from spec
  - Existing code without feature_list.json: Uses onboarding agent to analyze code
  - Has feature_list.json: Continues development with coding agent

Environment Variables:
  ANTHROPIC_API_KEY    Your Anthropic API key (required)
        """,
	)

	parser.add_argument(
		"--project-dir",
		type=Path,
		required=True,
		help="Directory for the project (required)",
	)

	parser.add_argument(
		"--spec",
		type=Path,
		default=None,
		help="Specification file (optional for existing codebases, required for new projects)",
	)

	parser.add_argument(
		"--max-iterations",
		type=int,
		default=None,
		help="Maximum number of agent iterations (default: unlimited)",
	)

	parser.add_argument(
		"--model",
		type=str,
		default=DEFAULT_MODEL,
		help=f"Claude model to use for all phases (default: {DEFAULT_MODEL})",
	)

	parser.add_argument(
		"--init-model",
		type=str,
		default=None,
		help="Model for initializer/onboarding phases (overrides --model for first session)",
	)

	parser.add_argument(
		"--code-model",
		type=str,
		default=None,
		help="Model for coding phases (overrides --model for coding sessions)",
	)

	parser.add_argument(
		"--idle-timeout",
		type=int,
		default=180,
		help="Abort session if no output for N seconds (default: 180). Set to 0 to disable.",
	)

	parser.add_argument(
		"--quit-on-abort",
		type=int,
		default=0,
		help="Quit after N consecutive failures (default: 0 = never quit, keep retrying).",
	)

	return parser.parse_args()


def main() -> None:
	"""Main entry point."""
	args = parse_args()

	if not os.environ.get("ANTHROPIC_API_KEY"):
		print("Error: ANTHROPIC_API_KEY environment variable not set")
		print("\nGet your API key from: https://console.anthropic.com/")
		print("\nThen set it:")
		print("  export ANTHROPIC_API_KEY='your-api-key-here'")
		return

	project_dir = args.project_dir
	if not str(project_dir).startswith("generations/"):
		if project_dir.is_absolute():
			pass
		else:
			project_dir = Path("generations") / project_dir

	init_model = args.init_model if args.init_model else args.model
	code_model = args.code_model if args.code_model else args.model

	try:
		asyncio.run(
			run_autonomous_agent(
				project_dir=project_dir,
				init_model=init_model,
				code_model=code_model,
				max_iterations=args.max_iterations,
				idle_timeout=args.idle_timeout if args.idle_timeout > 0 else None,
				quit_on_abort=args.quit_on_abort if args.quit_on_abort > 0 else None,
				spec_file=args.spec,
			)
		)
	except KeyboardInterrupt:
		print("\n\nInterrupted by user")
		print("To resume, run the same command again")
	except Exception as exc:  # noqa: BLE001
		print(f"\nFatal error: {exc}")
		raise
