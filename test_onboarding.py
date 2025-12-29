"""
Tests for onboarding detection logic.
"""

import tempfile
from pathlib import Path

from agent import has_existing_codebase


def test_empty_directory():
    """Test that an empty directory is not considered an existing codebase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        assert not has_existing_codebase(project_dir)


def test_nonexistent_directory():
    """Test that a nonexistent directory is not considered an existing codebase."""
    project_dir = Path("/nonexistent/path")
    assert not has_existing_codebase(project_dir)


def test_only_tracking_files():
    """Test that a directory with only tracking files is not considered an existing codebase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create .aidd directory with tracking files
        aidd_dir = project_dir / ".aidd"
        aidd_dir.mkdir()
        (aidd_dir / "feature_list.json").write_text("{}")
        (aidd_dir / "spec.txt").write_text("spec")
        (aidd_dir / "init.sh").write_text("#!/bin/bash")
        (aidd_dir / "claude-progress.txt").write_text("progress")

        assert not has_existing_codebase(project_dir)


def test_with_git_only():
    """Test that a directory with only .git is not considered an existing codebase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create .git directory
        git_dir = project_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git config")

        assert not has_existing_codebase(project_dir)


def test_with_node_modules():
    """Test that node_modules alone doesn't count as existing code."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create node_modules
        node_modules = project_dir / "node_modules"
        node_modules.mkdir()
        (node_modules / "some-package").mkdir()

        assert not has_existing_codebase(project_dir)


def test_with_actual_code_file():
    """Test that a directory with actual code is considered an existing codebase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create an actual code file
        (project_dir / "index.js").write_text("console.log('hello');")

        assert has_existing_codebase(project_dir)


def test_with_package_json():
    """Test that a directory with package.json is considered an existing codebase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create package.json
        (project_dir / "package.json").write_text('{"name": "test"}')

        assert has_existing_codebase(project_dir)


def test_with_src_directory():
    """Test that a directory with src/ is considered an existing codebase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create src directory with code
        src_dir = project_dir / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('hello')")

        assert has_existing_codebase(project_dir)


def test_with_readme():
    """Test that a directory with README is considered an existing codebase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create README
        (project_dir / "README.md").write_text("# My Project")

        assert has_existing_codebase(project_dir)


def test_mixed_tracking_and_code():
    """Test that tracking files + code is considered an existing codebase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create .auto directory with tracking files
        auto_dir = project_dir / ".auto"
        auto_dir.mkdir()
        (auto_dir / "feature_list.json").write_text("{}")
        (auto_dir / "spec.txt").write_text("spec")

        # Create actual code
        (project_dir / "app.py").write_text("print('hello')")

        assert has_existing_codebase(project_dir)


def test_hidden_files_ignored():
    """Test that hidden files (except .git) are ignored."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create hidden files that should be ignored
        (project_dir / ".DS_Store").write_text("mac metadata")
        (project_dir / ".vscode").mkdir()
        (project_dir / ".idea").mkdir()

        # Should not be considered existing code
        assert not has_existing_codebase(project_dir)


if __name__ == "__main__":
    # Run all tests
    test_empty_directory()
    test_nonexistent_directory()
    test_only_tracking_files()
    test_with_git_only()
    test_with_node_modules()
    test_with_actual_code_file()
    test_with_package_json()
    test_with_src_directory()
    test_with_readme()
    test_mixed_tracking_and_code()
    test_hidden_files_ignored()

    print("All onboarding detection tests passed!")
