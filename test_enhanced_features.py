"""
Tests for enhanced feature list structure and progress display.
"""

import json
import tempfile
from pathlib import Path
from progress import (
    load_feature_list,
    count_passing_tests,
    get_feature_breakdown,
    print_progress_summary,
)


def create_test_feature_list(project_dir: Path, features: list) -> None:
    """Helper to create a test feature_list.json."""
    feature_file = project_dir / "feature_list.json"
    with open(feature_file, "w") as f:
        json.dump(features, f, indent=2)


class TestEnhancedFeatureList:
    """Tests for enhanced feature list structure."""

    def test_load_feature_list_exists(self):
        """Test loading an existing feature list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            features = [{"description": "test", "passes": False}]
            create_test_feature_list(project_dir, features)

            result = load_feature_list(project_dir)
            assert result == features

    def test_load_feature_list_not_exists(self):
        """Test loading when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            result = load_feature_list(project_dir)
            assert result is None

    def test_get_feature_breakdown_by_area(self):
        """Test breakdown by area."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            features = [
                {"area": "backend", "passes": True},
                {"area": "backend", "passes": False},
                {"area": "frontend", "passes": True},
                {"area": "frontend", "passes": True},
                {"area": "database", "passes": False},
            ]
            create_test_feature_list(project_dir, features)

            breakdown = get_feature_breakdown(project_dir)

            assert breakdown["by_area"]["backend"]["total"] == 2
            assert breakdown["by_area"]["backend"]["passing"] == 1
            assert breakdown["by_area"]["frontend"]["total"] == 2
            assert breakdown["by_area"]["frontend"]["passing"] == 2
            assert breakdown["by_area"]["database"]["total"] == 1
            assert breakdown["by_area"]["database"]["passing"] == 0

    def test_get_feature_breakdown_by_priority(self):
        """Test breakdown by priority."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            features = [
                {"priority": "critical", "passes": True},
                {"priority": "critical", "passes": False},
                {"priority": "high", "passes": True},
                {"priority": "medium", "passes": False},
                {"priority": "low", "passes": False},
            ]
            create_test_feature_list(project_dir, features)

            breakdown = get_feature_breakdown(project_dir)

            assert breakdown["by_priority"]["critical"]["total"] == 2
            assert breakdown["by_priority"]["critical"]["passing"] == 1
            assert breakdown["by_priority"]["high"]["total"] == 1
            assert breakdown["by_priority"]["high"]["passing"] == 1
            assert breakdown["by_priority"]["medium"]["total"] == 1
            assert breakdown["by_priority"]["medium"]["passing"] == 0
            assert breakdown["by_priority"]["low"]["total"] == 1
            assert breakdown["by_priority"]["low"]["passing"] == 0

    def test_get_feature_breakdown_by_status(self):
        """Test breakdown by status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            features = [
                {"status": "open", "passes": False},
                {"status": "open", "passes": False},
                {"status": "in_progress", "passes": False},
                {"status": "resolved", "passes": True},
                {"status": "resolved", "passes": True},
                {"status": "deferred", "passes": False},
            ]
            create_test_feature_list(project_dir, features)

            breakdown = get_feature_breakdown(project_dir)

            assert breakdown["by_status"]["open"] == 2
            assert breakdown["by_status"]["in_progress"] == 1
            assert breakdown["by_status"]["resolved"] == 2
            assert breakdown["by_status"]["deferred"] == 1

    def test_get_feature_breakdown_by_category(self):
        """Test breakdown by category."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            features = [
                {"category": "functional", "passes": False},
                {"category": "functional", "passes": True},
                {"category": "style", "passes": False},
                {"category": "security", "passes": True},
            ]
            create_test_feature_list(project_dir, features)

            breakdown = get_feature_breakdown(project_dir)

            assert breakdown["by_category"]["functional"] == 2
            assert breakdown["by_category"]["style"] == 1
            assert breakdown["by_category"]["security"] == 1

    def test_get_feature_breakdown_empty(self):
        """Test breakdown with no feature list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            breakdown = get_feature_breakdown(project_dir)
            assert breakdown == {}

    def test_count_passing_with_enhanced_fields(self):
        """Test that count_passing_tests works with enhanced feature format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            features = [
                {
                    "area": "backend",
                    "category": "functional",
                    "priority": "critical",
                    "status": "resolved",
                    "passes": True,
                },
                {
                    "area": "frontend",
                    "category": "style",
                    "priority": "medium",
                    "status": "open",
                    "passes": False,
                },
                {
                    "area": "database",
                    "category": "functional",
                    "priority": "high",
                    "status": "in_progress",
                    "passes": False,
                },
            ]
            create_test_feature_list(project_dir, features)

            passing, total = count_passing_tests(project_dir)

            assert passing == 1
            assert total == 3

    def test_backward_compatibility_simple_format(self):
        """Test that simple format (without enhanced fields) still works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            # Old simple format
            features = [
                {"category": "functional", "description": "Test 1", "passes": True},
                {"category": "style", "description": "Test 2", "passes": False},
            ]
            create_test_feature_list(project_dir, features)

            passing, total = count_passing_tests(project_dir)
            assert passing == 1
            assert total == 2

            breakdown = get_feature_breakdown(project_dir)
            # Should have "unknown" for missing fields
            assert "unknown" in breakdown["by_area"]
            assert "unknown" in breakdown["by_priority"]
            assert "unknown" in breakdown["by_status"]


def run_simple_tests():
    """Run tests without pytest for basic validation."""
    print("Running enhanced feature list tests...")

    test_class = TestEnhancedFeatureList()

    test_class.test_load_feature_list_exists()
    print("  - Load feature list (exists): OK")

    test_class.test_load_feature_list_not_exists()
    print("  - Load feature list (not exists): OK")

    test_class.test_get_feature_breakdown_by_area()
    print("  - Breakdown by area: OK")

    test_class.test_get_feature_breakdown_by_priority()
    print("  - Breakdown by priority: OK")

    test_class.test_get_feature_breakdown_by_status()
    print("  - Breakdown by status: OK")

    test_class.test_get_feature_breakdown_by_category()
    print("  - Breakdown by category: OK")

    test_class.test_get_feature_breakdown_empty()
    print("  - Breakdown empty: OK")

    test_class.test_count_passing_with_enhanced_fields()
    print("  - Count passing with enhanced fields: OK")

    test_class.test_backward_compatibility_simple_format()
    print("  - Backward compatibility: OK")

    print("All enhanced feature list tests passed!")


if __name__ == "__main__":
    run_simple_tests()
