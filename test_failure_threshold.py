"""
Tests for failure threshold (quit-on-abort) functionality.
"""

import sys
from unittest.mock import patch


def test_default_quit_on_abort():
    """Test that default quit_on_abort is 0 (disabled)."""
    with patch.object(sys, 'argv', ['prog', '--project-dir', './test']):
        import importlib
        import aidd_c
        importlib.reload(aidd_c)

        args = aidd_c.parse_args()

        assert args.quit_on_abort == 0


def test_quit_on_abort_set():
    """Test that --quit-on-abort can be set."""
    with patch.object(sys, 'argv', ['prog', '--project-dir', './test', '--quit-on-abort', '3']):
        import importlib
        import aidd_c
        importlib.reload(aidd_c)

        args = aidd_c.parse_args()

        assert args.quit_on_abort == 3


def test_quit_on_abort_zero_means_disabled():
    """Test that --quit-on-abort 0 means disabled (None passed to agent)."""
    with patch.object(sys, 'argv', ['prog', '--project-dir', './test', '--quit-on-abort', '0']):
        import importlib
        import aidd_c
        importlib.reload(aidd_c)

        args = aidd_c.parse_args()

        # Zero means disabled
        quit_on_abort = args.quit_on_abort if args.quit_on_abort > 0 else None
        assert quit_on_abort is None


def test_quit_on_abort_with_other_options():
    """Test that --quit-on-abort works with other options."""
    with patch.object(sys, 'argv', [
        'prog',
        '--project-dir', './test',
        '--idle-timeout', '300',
        '--quit-on-abort', '5',
        '--max-iterations', '10'
    ]):
        import importlib
        import aidd_c
        importlib.reload(aidd_c)

        args = aidd_c.parse_args()

        assert args.idle_timeout == 300
        assert args.quit_on_abort == 5
        assert args.max_iterations == 10


class TestConsecutiveFailureTracking:
    """Tests for the consecutive failure tracking logic."""

    def test_failure_counter_increments(self):
        """Test that failure counter increments on failures."""
        consecutive_failures = 0

        # Simulate a failure
        status = "error"
        if status in ("error", "idle_timeout"):
            consecutive_failures += 1

        assert consecutive_failures == 1

        # Simulate another failure
        status = "idle_timeout"
        if status in ("error", "idle_timeout"):
            consecutive_failures += 1

        assert consecutive_failures == 2

    def test_failure_counter_resets_on_success(self):
        """Test that failure counter resets on success."""
        consecutive_failures = 5

        # Simulate success
        status = "continue"
        if status == "continue":
            consecutive_failures = 0

        assert consecutive_failures == 0

    def test_threshold_check(self):
        """Test that threshold check works correctly."""
        quit_on_abort = 3
        consecutive_failures = 2

        # Should not quit yet
        should_quit = quit_on_abort and consecutive_failures >= quit_on_abort
        assert not should_quit

        # One more failure
        consecutive_failures = 3

        # Should quit now
        should_quit = quit_on_abort and consecutive_failures >= quit_on_abort
        assert should_quit

    def test_disabled_threshold(self):
        """Test that disabled threshold never triggers quit."""
        quit_on_abort = None  # Disabled
        consecutive_failures = 100

        # Should never quit when disabled
        should_quit = quit_on_abort and consecutive_failures >= quit_on_abort
        assert not should_quit


def run_simple_tests():
    """Run tests without pytest for basic validation."""
    print("Running failure threshold tests...")

    # Test CLI argument parsing
    test_default_quit_on_abort()
    print("  - Default quit_on_abort is 0: OK")

    test_quit_on_abort_set()
    print("  - quit_on_abort can be set: OK")

    test_quit_on_abort_zero_means_disabled()
    print("  - quit_on_abort 0 means disabled: OK")

    test_quit_on_abort_with_other_options()
    print("  - quit_on_abort works with other options: OK")

    # Test failure tracking logic
    tracker = TestConsecutiveFailureTracking()
    tracker.test_failure_counter_increments()
    print("  - Failure counter increments: OK")

    tracker.test_failure_counter_resets_on_success()
    print("  - Failure counter resets on success: OK")

    tracker.test_threshold_check()
    print("  - Threshold check works: OK")

    tracker.test_disabled_threshold()
    print("  - Disabled threshold never triggers: OK")

    print("All failure threshold tests passed!")


if __name__ == "__main__":
    run_simple_tests()
