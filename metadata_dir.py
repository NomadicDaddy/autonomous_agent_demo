"""
Metadata Directory Utilities
============================

Functions to find or create the appropriate metadata directory (.auto, .autok, .automaker)
"""

from pathlib import Path
from typing import Optional


def find_or_create_metadata_dir(project_dir: Path) -> Path:
    """
    Find existing metadata directory or create .auto as default.

    Checks for directories in order: .auto, .autok, .automaker
    If none exist, creates .auto and returns it.

    Args:
        project_dir: The project directory

    Returns:
        Path to the metadata directory
    """
    # Check for existing directories in order of preference
    for dir_name in [".auto", ".autok", ".automaker"]:
        metadata_dir = project_dir / dir_name
        if metadata_dir.exists():
            return metadata_dir

    # Create .auto as default
    metadata_dir = project_dir / ".auto"
    metadata_dir.mkdir(exist_ok=True)
    return metadata_dir


def get_metadata_dir_name(project_dir: Path) -> Optional[str]:
    """
    Get the name of the existing metadata directory.

    Args:
        project_dir: The project directory

    Returns:
        Name of the metadata directory (.auto, .autok, .automaker) or None if none exist
    """
    for dir_name in [".auto", ".autok", ".automaker"]:
        if (project_dir / dir_name).exists():
            return dir_name
    return None
