"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
"""

import json
from collections import Counter
from pathlib import Path
from typing import Optional


def load_feature_list(project_dir: Path) -> Optional[list]:
    """
    Load feature_list.json from project directory.

    Args:
        project_dir: Directory containing feature_list.json

    Returns:
        List of features or None if file doesn't exist or is invalid
    """
    tests_file = project_dir / "feature_list.json"

    if not tests_file.exists():
        return None

    try:
        with open(tests_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def count_passing_tests(project_dir: Path) -> tuple[int, int]:
    """
    Count passing and total tests in feature_list.json.

    Args:
        project_dir: Directory containing feature_list.json

    Returns:
        (passing_count, total_count)
    """
    tests = load_feature_list(project_dir)

    if tests is None:
        return 0, 0

    total = len(tests)
    passing = sum(1 for test in tests if test.get("passes", False))

    return passing, total


def get_feature_breakdown(project_dir: Path) -> dict:
    """
    Get detailed breakdown of features by area, priority, and status.

    Args:
        project_dir: Directory containing feature_list.json

    Returns:
        Dictionary with breakdown statistics
    """
    tests = load_feature_list(project_dir)

    if tests is None:
        return {}

    # Count by area
    area_counts = Counter(test.get("area", "unknown") for test in tests)
    area_passing = Counter(
        test.get("area", "unknown") for test in tests if test.get("passes", False)
    )

    # Count by priority
    priority_counts = Counter(test.get("priority", "unknown") for test in tests)
    priority_passing = Counter(
        test.get("priority", "unknown") for test in tests if test.get("passes", False)
    )

    # Count by status
    status_counts = Counter(test.get("status", "unknown") for test in tests)

    # Count by category
    category_counts = Counter(test.get("category", "unknown") for test in tests)

    return {
        "by_area": {
            area: {"total": count, "passing": area_passing.get(area, 0)}
            for area, count in area_counts.items()
        },
        "by_priority": {
            priority: {"total": count, "passing": priority_passing.get(priority, 0)}
            for priority, count in priority_counts.items()
        },
        "by_status": dict(status_counts),
        "by_category": dict(category_counts),
    }


def print_session_header(session_num: int, is_initializer: bool) -> None:
    """Print a formatted header for the session."""
    session_type = "INITIALIZER" if is_initializer else "CODING AGENT"

    print("\n" + "=" * 70)
    print(f"  SESSION {session_num}: {session_type}")
    print("=" * 70)
    print()


def print_progress_summary(project_dir: Path, verbose: bool = False) -> None:
    """
    Print a summary of current progress.

    Args:
        project_dir: Directory containing feature_list.json
        verbose: If True, show detailed breakdown by area/priority/status
    """
    passing, total = count_passing_tests(project_dir)

    if total == 0:
        print("\nProgress: feature_list.json not yet created")
        return

    percentage = (passing / total) * 100
    print(f"\nProgress: {passing}/{total} tests passing ({percentage:.1f}%)")

    # Get breakdown for enhanced display
    breakdown = get_feature_breakdown(project_dir)

    if not breakdown:
        return

    # Show status summary (always shown)
    by_status = breakdown.get("by_status", {})
    if by_status and "unknown" not in by_status:
        status_parts = []
        for status in ["open", "in_progress", "resolved", "deferred"]:
            if status in by_status:
                status_parts.append(f"{by_status[status]} {status}")
        if status_parts:
            print(f"Status: {', '.join(status_parts)}")

    # Show priority breakdown (always shown if available)
    by_priority = breakdown.get("by_priority", {})
    if by_priority and "unknown" not in by_priority:
        priority_order = ["critical", "high", "medium", "low"]
        priority_parts = []
        for priority in priority_order:
            if priority in by_priority:
                info = by_priority[priority]
                priority_parts.append(f"{info['passing']}/{info['total']} {priority}")
        if priority_parts:
            print(f"By priority: {', '.join(priority_parts)}")

    # Verbose output: show area breakdown
    if verbose:
        by_area = breakdown.get("by_area", {})
        if by_area and "unknown" not in by_area:
            print("\nBreakdown by area:")
            area_order = ["database", "backend", "frontend", "testing", "security", "devex", "docs"]
            for area in area_order:
                if area in by_area:
                    info = by_area[area]
                    pct = (info["passing"] / info["total"] * 100) if info["total"] > 0 else 0
                    print(f"  {area:12}: {info['passing']:3}/{info['total']:3} ({pct:5.1f}%)")
