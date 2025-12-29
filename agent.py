"""
Agent Session Logic
===================

Core agent interaction functions for running autonomous coding sessions.
"""

import asyncio
from pathlib import Path
from typing import Optional

from claude_code_sdk import ClaudeSDKClient

from client import create_client
from metadata_dir import find_or_create_metadata_dir
from progress import print_session_header, print_progress_summary
from prompts import get_initializer_prompt, get_coding_prompt, get_onboarding_prompt, copy_spec_to_project


# Configuration
AUTO_CONTINUE_DELAY_SECONDS = 3
DEFAULT_IDLE_TIMEOUT = 180  # Default idle timeout in seconds


class IdleTimeoutError(Exception):
    """Raised when the agent session exceeds the idle timeout."""
    pass


async def async_iter_with_timeout(async_iter, timeout_seconds: Optional[float]):
    """
    Wrap an async iterator with an idle timeout.

    If no item is yielded within timeout_seconds, raises IdleTimeoutError.
    If timeout_seconds is None, no timeout is applied.

    Args:
        async_iter: The async iterator to wrap
        timeout_seconds: Maximum seconds to wait for each item (None to disable)

    Yields:
        Items from the underlying async iterator

    Raises:
        IdleTimeoutError: If timeout_seconds passes without receiving an item
    """
    if timeout_seconds is None:
        # No timeout - just pass through
        async for item in async_iter:
            yield item
        return

    # Get the async iterator
    aiter = async_iter.__aiter__()

    while True:
        try:
            # Wait for the next item with timeout
            item = await asyncio.wait_for(aiter.__anext__(), timeout=timeout_seconds)
            yield item
        except StopAsyncIteration:
            # Iterator exhausted normally
            return
        except asyncio.TimeoutError:
            # Idle timeout exceeded
            raise IdleTimeoutError(
                f"Session idle timeout: no output received for {timeout_seconds} seconds"
            )


def has_existing_codebase(project_dir: Path) -> bool:
    """
    Check if the project directory has existing code (not just auto-claudecode artifacts).

    Returns True if there are files that suggest this is an existing codebase,
    False if it's empty or only has our tracking files.
    """
    if not project_dir.exists():
        return False

    # Files to ignore when checking for existing code
    ignored_patterns = {
        '.auto',
        '.autok',
        '.automaker',
        '.git',
        '.DS_Store',
        '__pycache__',
        'node_modules',
        '.vscode',
        '.idea',
    }

    # Check for any non-ignored files or directories
    for item in project_dir.iterdir():
        # Skip hidden files except .git
        if item.name.startswith('.') and item.name != '.git':
            continue

        # Skip our tracking files
        if item.name in ignored_patterns:
            continue

        # Found a file/directory that suggests existing code
        return True

    return False


async def run_agent_session(
    client: ClaudeSDKClient,
    message: str,
    project_dir: Path,
    idle_timeout: Optional[float] = None,
) -> tuple[str, str]:
    """
    Run a single agent session using Claude Agent SDK.

    Args:
        client: Claude SDK client
        message: The prompt to send
        project_dir: Project directory path
        idle_timeout: Seconds to wait for output before aborting (None to disable)

    Returns:
        (status, response_text) where status is:
        - "continue" if agent should continue working
        - "idle_timeout" if session was aborted due to idle timeout
        - "error" if an error occurred
    """
    if idle_timeout:
        print(f"Sending prompt to Claude Agent SDK (idle timeout: {idle_timeout}s)...\n")
    else:
        print("Sending prompt to Claude Agent SDK...\n")

    try:
        # Send the query
        await client.query(message)

        # Collect response text and show tool use
        # Wrap the response iterator with idle timeout detection
        response_text = ""
        async for msg in async_iter_with_timeout(client.receive_response(), idle_timeout):
            msg_type = type(msg).__name__

            # Handle AssistantMessage (text and tool use)
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        print(f"\n[Tool: {block.name}]", flush=True)
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            if len(input_str) > 200:
                                print(f"   Input: {input_str[:200]}...", flush=True)
                            else:
                                print(f"   Input: {input_str}", flush=True)

            # Handle UserMessage (tool results)
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)

                        # Check if command was blocked by security hook
                        if "blocked" in str(result_content).lower():
                            print(f"   [BLOCKED] {result_content}", flush=True)
                        elif is_error:
                            # Show errors (truncated)
                            error_str = str(result_content)[:500]
                            print(f"   [Error] {error_str}", flush=True)
                        else:
                            # Tool succeeded - just show brief confirmation
                            print("   [Done]", flush=True)

        print("\n" + "-" * 70 + "\n")
        return "continue", response_text

    except IdleTimeoutError as e:
        print(f"\n\n{'=' * 70}")
        print(f"  IDLE TIMEOUT: {e}")
        print(f"{'=' * 70}\n")
        return "idle_timeout", str(e)

    except Exception as e:
        print(f"Error during agent session: {e}")
        return "error", str(e)


async def run_autonomous_agent(
    project_dir: Path,
    init_model: str,
    code_model: str,
    max_iterations: Optional[int] = None,
    idle_timeout: Optional[int] = None,
    quit_on_abort: Optional[int] = None,
    spec_file: Optional[Path] = None,
) -> None:
    """
    Run the autonomous agent loop.

    Args:
        project_dir: Directory for the project
        init_model: Claude model for initializer/onboarding phases
        code_model: Claude model for coding phases
        max_iterations: Maximum number of iterations (None for unlimited)
        idle_timeout: Idle timeout in seconds (None for no timeout)
        quit_on_abort: Quit after N consecutive failures (None for never quit)
        spec_file: Optional specification file path
    """
    print("\n" + "=" * 70)
    print("  AUTONOMOUS CODING AGENT DEMO")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    if init_model == code_model:
        print(f"Model: {init_model}")
    else:
        print(f"Init/Onboarding model: {init_model}")
        print(f"Coding model: {code_model}")
    if max_iterations:
        print(f"Max iterations: {max_iterations}")
    else:
        print("Max iterations: Unlimited (will run until completion)")
    if idle_timeout:
        print(f"Idle timeout: {idle_timeout}s")
    if quit_on_abort:
        print(f"Quit on abort: after {quit_on_abort} consecutive failures")
    print()

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Find or create metadata directory
    metadata_dir = find_or_create_metadata_dir(project_dir)
    tests_file = metadata_dir / "feature_list.json"
    spec_file_path = metadata_dir / "spec.txt"
    has_existing_code = has_existing_codebase(project_dir)
    is_first_run = not tests_file.exists()

    # Determine session type
    session_type = None  # 'initializer', 'onboarding', or 'coding'

    if is_first_run and has_existing_code:
        # Existing codebase without feature_list.json - need onboarding
        session_type = 'onboarding'
        print("Existing codebase detected - will use onboarding agent")
        print()
        print("=" * 70)
        print("  NOTE: Onboarding session takes 10-20+ minutes!")
        print("  The agent is analyzing your codebase and generating test cases.")
        print("  This may appear to hang - it's working. Watch for [Tool: ...] output.")
        print("=" * 70)
        print()
    elif is_first_run and not has_existing_code:
        # Empty directory - fresh start
        session_type = 'initializer'
        print("Fresh start - will use initializer agent")
        print()
        print("=" * 70)
        print("  NOTE: First session takes 10-20+ minutes!")
        print("  The agent is generating 200 detailed test cases.")
        print("  This may appear to hang - it's working. Watch for [Tool: ...] output.")
        print("=" * 70)
        print()
        # Copy the app spec into the project directory for the agent to read
        copy_spec_to_project(project_dir, spec_file)
    else:
        # Continuing existing project
        session_type = 'coding'
        print("Continuing existing project")
        print_progress_summary(project_dir)

    # Main loop
    iteration = 0
    consecutive_failures = 0  # Track consecutive failures for quit_on_abort

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            print(f"\nReached max iterations ({max_iterations})")
            print("To continue, run the script again without --max-iterations")
            break

        # Print session header
        is_first_session = (iteration == 1)
        print_session_header(iteration, is_first_session)

        # Choose prompt and model based on session type
        if session_type == 'initializer':
            prompt = get_initializer_prompt()
            current_model = init_model
            session_type = 'coding'  # Switch to coding after initializer
        elif session_type == 'onboarding':
            prompt = get_onboarding_prompt()
            current_model = init_model
            session_type = 'coding'  # Switch to coding after onboarding
        else:  # session_type == 'coding'
            prompt = get_coding_prompt()
            current_model = code_model

        # Create client with the appropriate model (fresh context)
        client = create_client(project_dir, current_model)

        # Run session with async context manager
        async with client:
            status, response = await run_agent_session(
                client, prompt, project_dir, idle_timeout=idle_timeout
            )

        # Handle status and track failures
        if status == "continue":
            # Success - reset failure counter
            consecutive_failures = 0
            print(f"\nAgent will auto-continue in {AUTO_CONTINUE_DELAY_SECONDS}s...")
            print_progress_summary(project_dir)
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "idle_timeout":
            # Failure - increment counter
            consecutive_failures += 1
            print("\nSession aborted due to idle timeout")
            print("This usually means the agent got stuck or is waiting for something.")

            # Check if we should quit
            if quit_on_abort and consecutive_failures >= quit_on_abort:
                print(f"\n{'=' * 70}")
                print(f"  ABORTING: {consecutive_failures} consecutive failures reached threshold ({quit_on_abort})")
                print(f"{'=' * 70}")
                print("\nTo continue, run the script again or increase --quit-on-abort")
                break

            print(f"Consecutive failures: {consecutive_failures}" +
                  (f"/{quit_on_abort}" if quit_on_abort else ""))
            print("Will retry with a fresh session...")
            print_progress_summary(project_dir)
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "error":
            # Failure - increment counter
            consecutive_failures += 1
            print("\nSession encountered an error")

            # Check if we should quit
            if quit_on_abort and consecutive_failures >= quit_on_abort:
                print(f"\n{'=' * 70}")
                print(f"  ABORTING: {consecutive_failures} consecutive failures reached threshold ({quit_on_abort})")
                print(f"{'=' * 70}")
                print("\nTo continue, run the script again or increase --quit-on-abort")
                break

            print(f"Consecutive failures: {consecutive_failures}" +
                  (f"/{quit_on_abort}" if quit_on_abort else ""))
            print("Will retry with a fresh session...")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            print("\nPreparing next session...\n")
            await asyncio.sleep(1)

    # Final summary
    print("\n" + "=" * 70)
    print("  SESSION COMPLETE")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print_progress_summary(project_dir)

    # Print instructions for running the generated application
    print("\n" + "-" * 70)
    print("  TO RUN THE GENERATED APPLICATION:")
    print("-" * 70)
    print(f"\n  cd {project_dir.resolve()}")
    print("  ./init.sh           # Run the setup script")
    print("  # Or manually:")
    print("  npm install && npm run dev")
    print("\n  Then open http://localhost:3000 (or check init.sh for the URL)")
    print("-" * 70)

    print("\nDone!")
