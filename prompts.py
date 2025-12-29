"""
Prompt Loading Utilities
========================

Functions for loading prompt templates from the prompts directory.
"""

import shutil
from metadata_dir import find_or_create_metadata_dir
from pathlib import Path


PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{name}.md"
    return prompt_path.read_text()


def get_initializer_prompt() -> str:
    """Load the initializer prompt."""
    return load_prompt("initializer")


def get_coding_prompt() -> str:
    """Load the coding agent prompt."""
    return load_prompt("coding")


def get_onboarding_prompt() -> str:
    """Load the onboarding agent prompt for existing codebases."""
    return load_prompt("onboarding")


def copy_spec_to_project(project_dir: Path, spec_source_path: Path = None) -> None:
    """Copy the app spec file into the project directory for the agent to read."""
    # Find or create metadata directory
    metadata_dir = find_or_create_metadata_dir(project_dir)

    if spec_source_path:
        # Use custom spec file provided by user
        spec_source = spec_source_path
    else:
        # Use default spec file
        spec_source = Path(__file__).parent / "specs" / "app_spec.txt"

    spec_dest = metadata_dir / "spec.txt"
    if not spec_dest.exists():
        shutil.copy(spec_source, spec_dest)
        print(f"Copied spec.txt to {metadata_dir.name} directory from {spec_source}")
