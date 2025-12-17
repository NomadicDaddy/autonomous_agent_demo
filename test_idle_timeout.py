"""
Tests for idle timeout functionality.
"""

import asyncio
import pytest
from agent import async_iter_with_timeout, IdleTimeoutError


async def slow_async_generator(items, delay_between_items=0.1):
    """Helper: async generator that yields items with a delay."""
    for item in items:
        await asyncio.sleep(delay_between_items)
        yield item


async def stalling_async_generator(items, stall_after=2, stall_duration=10):
    """Helper: async generator that stalls after yielding N items."""
    for i, item in enumerate(items):
        if i >= stall_after:
            # Stall indefinitely (or for a long time)
            await asyncio.sleep(stall_duration)
        yield item


class TestAsyncIterWithTimeout:
    """Tests for the async_iter_with_timeout function."""

    @pytest.mark.asyncio
    async def test_no_timeout_passthrough(self):
        """Test that None timeout passes through all items."""
        items = [1, 2, 3, 4, 5]
        result = []
        async for item in async_iter_with_timeout(slow_async_generator(items, 0.01), None):
            result.append(item)
        assert result == items

    @pytest.mark.asyncio
    async def test_fast_items_no_timeout(self):
        """Test that fast items don't trigger timeout."""
        items = [1, 2, 3, 4, 5]
        result = []
        # Items arrive every 0.01s, timeout is 1s - should never timeout
        async for item in async_iter_with_timeout(slow_async_generator(items, 0.01), 1.0):
            result.append(item)
        assert result == items

    @pytest.mark.asyncio
    async def test_timeout_triggers_on_stall(self):
        """Test that timeout triggers when items stop arriving."""
        items = [1, 2, 3, 4, 5]
        result = []
        # Timeout of 0.1s, stall after 2 items for 10 seconds
        with pytest.raises(IdleTimeoutError) as excinfo:
            async for item in async_iter_with_timeout(
                stalling_async_generator(items, stall_after=2, stall_duration=10),
                timeout_seconds=0.2
            ):
                result.append(item)

        # Should have gotten the first 2 items before timeout
        assert result == [1, 2]
        assert "0.2 seconds" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_empty_iterator(self):
        """Test that empty iterator works correctly."""
        result = []
        async for item in async_iter_with_timeout(slow_async_generator([], 0.01), 1.0):
            result.append(item)
        assert result == []

    @pytest.mark.asyncio
    async def test_single_item(self):
        """Test with a single item."""
        result = []
        async for item in async_iter_with_timeout(slow_async_generator([42], 0.01), 1.0):
            result.append(item)
        assert result == [42]

    @pytest.mark.asyncio
    async def test_timeout_message_format(self):
        """Test that timeout error message is formatted correctly."""
        with pytest.raises(IdleTimeoutError) as excinfo:
            async for _ in async_iter_with_timeout(
                stalling_async_generator([1], stall_after=0, stall_duration=10),
                timeout_seconds=0.1
            ):
                pass

        assert "idle timeout" in str(excinfo.value).lower()
        assert "0.1" in str(excinfo.value)


def test_idle_timeout_error_is_exception():
    """Test that IdleTimeoutError is a proper exception."""
    error = IdleTimeoutError("test message")
    assert str(error) == "test message"
    assert isinstance(error, Exception)


# Simple tests that can run without pytest
def run_simple_tests():
    """Run tests without pytest for basic validation."""

    async def test_basic_passthrough():
        items = [1, 2, 3]
        result = []
        async for item in async_iter_with_timeout(slow_async_generator(items, 0.01), None):
            result.append(item)
        assert result == items, f"Expected {items}, got {result}"
        print("  - Basic passthrough: OK")

    async def test_timeout_triggers():
        result = []
        try:
            async for item in async_iter_with_timeout(
                stalling_async_generator([1, 2, 3], stall_after=1, stall_duration=10),
                timeout_seconds=0.2
            ):
                result.append(item)
            assert False, "Should have raised IdleTimeoutError"
        except IdleTimeoutError as e:
            assert result == [1], f"Expected [1], got {result}"
            assert "0.2" in str(e), f"Expected '0.2' in error message, got: {e}"
            print("  - Timeout triggers on stall: OK")

    async def test_no_timeout_with_fast_items():
        items = list(range(10))
        result = []
        async for item in async_iter_with_timeout(slow_async_generator(items, 0.01), 1.0):
            result.append(item)
        assert result == items, f"Expected {items}, got {result}"
        print("  - No timeout with fast items: OK")

    print("Running idle timeout tests...")
    asyncio.run(test_basic_passthrough())
    asyncio.run(test_timeout_triggers())
    asyncio.run(test_no_timeout_with_fast_items())
    print("All idle timeout tests passed!")


if __name__ == "__main__":
    run_simple_tests()
