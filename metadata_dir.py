"""
Metadata Directory Utilities
============================

Functions to find or create the appropriate metadata directory (.aidd, .autok, .automaker)
"""

from pathlib import Path
from typing import Optional


def find_or_create_metadata_dir(project_dir: Path) -> Path:
    """
    Find existing metadata directory or create .aidd as default.

    Checks for directories in order: .aidd, .autok, .automaker
    If none exist, creates .aidd and returns it.

    Args:
        project_dir: The project directory

    Returns:
        Path to the metadata directory
    """
    # Check for existing directories in order of preference
    for dir_name in [".aidd", ".autok", ".automaker"]:
        metadata_dir = project_dir / dir_name
        if metadata_dir.exists():
            return metadata_dir

    # Create .aidd as default
    metadata_dir = project_dir / ".aidd"
    metadata_dir.mkdir(exist_ok=True)
    return metadata_dir


def get_metadata_dir_name(project_dir: Path) -> Optional[str]:
    """
    Get the name of the existing metadata directory.

    Args:
        project_dir: The project directory

    Returns:
        Name of the metadata directory (.aidd, .autok, .automaker) or None if none exist
    """
    for dir_name in [".aidd", ".autok", ".automaker"]:
        if (project_dir / dir_name).exists():
            return dir_name
    return None
