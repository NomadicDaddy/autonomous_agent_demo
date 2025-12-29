# AIDD-C - AI Development Driver: Claude

A minimal harness demonstrating long-running autonomous coding with the Claude Agent SDK. This demo implements a three-agent pattern (initializer/onboarding + coding agent) that can build complete applications over multiple sessions.

**New in v2.0:** Support for existing codebases! The agent can now analyze and continue development on existing projects, not just build from scratch.

## Prerequisites

**Required:** Install the latest versions of both Claude Code and the Claude Agent SDK:

```bash
# Install Claude Code CLI (latest version required)
npm install -g @anthropic-ai/claude-code

# Install Python dependencies
pip install -r requirements.txt
```

Verify your installations:
```bash
claude --version  # Should be latest version
pip show claude-code-sdk  # Check SDK is installed
```

**API Key:** Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Quick Start

**New Project (build from scratch):**
```bash
python aidd-c.py --project-dir ./my_project --spec ./specs/app_spec.txt
```

**Existing Codebase (analyze and continue):**
```bash
python aidd-c.py --project-dir ./path/to/existing/app
```

**Testing with limited iterations:**
```bash
python aidd-c.py --project-dir ./my_project --spec ./specs/app_spec.txt --max-iterations 3
```

## Important Timing Expectations

> **Warning: This demo takes a long time to run!**

- **First session (initialization):** The agent generates a metadata directory (`.auto`, `.autok`, or `.automaker`) with a `feature_list.json` containing 200 test cases. This takes several minutes and may appear to hang - this is normal. The agent is writing out all the features.

- **Subsequent sessions:** Each coding iteration can take **5-15 minutes** depending on complexity.

- **Full app:** Building all 200 features typically requires **many hours** of total runtime across multiple sessions.

**Tip:** The 200 features parameter in the prompts is designed for comprehensive coverage. If you want faster demos, you can modify `prompts/initializer.md` to reduce the feature count (e.g., 20-50 features for a quicker demo).

## How It Works

### Three-Agent Pattern

The system automatically detects which agent to use based on the project directory state:

1. **Initializer Agent (Session 1 - New Projects):**
   - Triggered when: Directory is empty or doesn't exist
   - Reads `spec.txt` from metadata directory, creates `feature_list.json` with 200 test cases
   - Sets up project structure and initializes git
   - Begins implementation if time permits

2. **Onboarding Agent (Session 1 - Existing Codebases):**
   - Triggered when: Directory has existing code but no metadata directory with `feature_list.json`
   - Analyzes the existing codebase to understand what's implemented
   - Creates or infers `spec.txt` from the code in the metadata directory
   - Creates `feature_list.json` with existing features marked as passing
   - Identifies missing features and technical debt
   - Prepares for continued development

3. **Coding Agent (Sessions 2+):**
   - Triggered when: `feature_list.json` exists in metadata directory
   - Picks up where previous session left off
   - Implements features one by one
   - Marks them as passing in `feature_list.json`
   - Works on both new and existing codebases

### Session Management

- Each session runs with a fresh context window
- Progress is persisted via metadata directory (`feature_list.json`) and git commits
- The agent auto-continues between sessions (3 second delay)
- Press `Ctrl+C` to pause; run the same command to resume

## Security Model

This demo uses a defense-in-depth security approach (see `security.py` and `client.py`):

1. **OS-level Sandbox:** Bash commands run in an isolated environment
2. **Filesystem Restrictions:** File operations restricted to the project directory only
3. **Bash Allowlist:** Only specific commands are permitted:
   - File inspection: `ls`, `cat`, `head`, `tail`, `wc`, `grep`
   - Node.js: `npm`, `node`
   - Version control: `git`
   - Process management: `ps`, `lsof`, `sleep`, `pkill` (dev processes only)

Commands not in the allowlist are blocked by the security hook.

## Project Structure

```
autonomous-coding/
├── aidd-c.py  # Main entry point
├── agent.py                  # Agent session logic
├── client.py                 # Claude SDK client configuration
├── security.py               # Bash command allowlist and validation
├── progress.py               # Progress tracking utilities
├── prompts.py                # Prompt loading utilities
├── prompts/
│   ├── initializer.md # First session prompt (new projects)
│   ├── onboarding.md  # First session prompt (existing codebases)
│   └── coding.md      # Continuation session prompt
├── specs/
│   └── app_spec.txt          # Application specification
└── requirements.txt          # Python dependencies
```

## Generated Project Structure

After running, your project directory will contain:

```
my_project/
├── .aidd/                      # or .autok/ or .automaker/ (whichever is found/created)
│   ├── feature_list.json         # Test cases (source of truth)
│   ├── spec.txt                  # Copied specification
│   ├── init.sh                   # Environment setup script
│   └── claude-progress.txt       # Session progress notes
├── .claude_settings.json     # Security settings
└── [application files]       # Generated application code
```

## Feature List Schema

The metadata directory's `feature_list.json` file uses an enhanced schema with rich metadata for better tracking:

```json
{
  "area": "backend",
  "category": "functional",
  "description": "User can log in with email and password",
  "priority": "critical",
  "status": "open",
  "created_at": "2025-01-15",
  "closed_at": null,
  "steps": [
    "Step 1: Navigate to login page",
    "Step 2: Enter credentials",
    "Step 3: Verify login success"
  ],
  "passes": false
}
```

**Field Definitions:**

| Field | Values | Description |
|-------|--------|-------------|
| `area` | `database`, `backend`, `frontend`, `testing`, `security`, `devex`, `docs` | System area |
| `category` | `functional`, `style`, `security`, `performance`, `accessibility` | Test type |
| `priority` | `critical`, `high`, `medium`, `low` | Implementation priority |
| `status` | `open`, `in_progress`, `resolved`, `deferred` | Current state |
| `created_at` | `YYYY-MM-DD` | Date feature was added |
| `closed_at` | `YYYY-MM-DD` or `null` | Date feature was completed |
| `steps` | Array of strings | Testing steps |
| `passes` | `true` or `false` | Whether feature passes testing |

**Progress Display:**

The agent displays progress summaries including:
- Overall passing/total counts
- Status breakdown (open, in_progress, resolved, deferred)
- Priority breakdown (critical, high, medium, low)

## Running the Generated Application

After the agent completes (or pauses), you can run the generated application:

```bash
cd generations/my_project

# Run the setup script created by the agent
./[metadata-dir]/init.sh

# Or manually (typical for Node.js apps):
npm install
npm run dev
```

The application will typically be available at `http://localhost:3000` or similar (check the agent's output or `[metadata-dir]/init.sh` for the exact URL).

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir` | Directory for the project (required) | None |
| `--spec` | Specification file (required for new projects) | None |
| `--max-iterations` | Max agent iterations | Unlimited |
| `--model` | Claude model for all phases | `claude-sonnet-4-5-20250929` |
| `--init-model` | Model for init/onboarding (overrides `--model`) | Same as `--model` |
| `--code-model` | Model for coding phases (overrides `--model`) | Same as `--model` |
| `--idle-timeout` | Abort session if no output for N seconds | `180` |
| `--quit-on-abort` | Quit after N consecutive failures | `0` (never) |

### Multi-Model Configuration

You can use different models for different phases to optimize cost and performance:

```bash
# Use Haiku 4.5 for setup (cheaper), Sonnet 4.5 for coding (more capable)
python aidd-c.py --project-dir ./my_project --spec ./specs/app_spec.txt \
  --init-model claude-haiku-4-5-20251001 \
  --code-model claude-sonnet-4-5-20250929

# Use Opus 4.5 for complex coding tasks
python aidd-c.py --project-dir ./my_project --spec ./specs/app_spec.txt \
  --code-model claude-opus-4-5-20251101
```

**Recommended configurations:**

| Use Case | Init Model | Code Model |
|----------|-----------|------------|
| Cost-optimized | `claude-haiku-4-5-20251001` | `claude-sonnet-4-5-20250929` |
| Balanced | `claude-sonnet-4-5-20250929` | `claude-sonnet-4-5-20250929` |
| Maximum quality | `claude-sonnet-4-5-20250929` | `claude-opus-4-5-20251101` |

### Idle Timeout

The idle timeout feature automatically detects and handles stuck agent sessions. If the agent produces no output for the specified number of seconds, the session is aborted and a fresh session is started.

```bash
# Use default 180-second idle timeout
python aidd-c.py --project-dir ./my_project

# Increase timeout for complex operations (5 minutes)
python aidd-c.py --project-dir ./my_project --idle-timeout 300

# Disable idle timeout entirely
python aidd-c.py --project-dir ./my_project --idle-timeout 0
```

**When to adjust idle timeout:**
- **Increase** if you're seeing false timeouts during long-running operations
- **Decrease** if you want faster detection of stuck sessions
- **Disable (0)** if you want the agent to run without time limits

### Failure Threshold

The failure threshold feature tracks consecutive failures (errors and idle timeouts) and can automatically quit after reaching a threshold. This prevents infinite retry loops when something is fundamentally broken.

```bash
# Default: never quit, keep retrying forever
python aidd-c.py --project-dir ./my_project

# Quit after 3 consecutive failures
python aidd-c.py --project-dir ./my_project --quit-on-abort 3

# Quit after 5 consecutive failures (more resilient)
python aidd-c.py --project-dir ./my_project --quit-on-abort 5
```

**How it works:**
- Counter increments on errors or idle timeouts
- Counter resets to 0 on successful session completion
- When counter reaches threshold, the agent stops
- Use `0` (default) to disable and keep retrying indefinitely

**When to use:**
- **Production runs:** Set to 3-5 to avoid wasting compute on broken sessions
- **Development/debugging:** Set to 0 to allow manual investigation
- **Unattended runs:** Set to a reasonable threshold to prevent runaway costs

## Customization

### Changing the Application

Edit `specs/app_spec.txt` to specify a different application to build.

### Adjusting Feature Count

Edit `prompts/initializer.md` and change the "200 features" requirement to a smaller number for faster demos.

### Modifying Allowed Commands

Edit `security.py` to add or remove commands from `ALLOWED_COMMANDS`.

## Troubleshooting

**"Appears to hang on first run"**
This is normal. The initializer agent is generating 200 detailed test cases, which takes significant time. Watch for `[Tool: ...]` output to confirm the agent is working.

**"Command blocked by security hook"**
The agent tried to run a command not in the allowlist. This is the security system working as intended. If needed, add the command to `ALLOWED_COMMANDS` in `security.py`.

**"API key not set"**
Ensure `ANTHROPIC_API_KEY` is exported in your shell environment.

## License

Internal Anthropic use.
