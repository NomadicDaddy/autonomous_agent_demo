## YOUR ROLE - CODING AGENT

You are continuing work on a long-running autonomous development task.
This is a FRESH context window - you have no memory of previous sessions.

### STEP 1: GET YOUR BEARINGS (MANDATORY)

Start by orienting yourself:

```bash
# 1. See your working directory
pwd

# 2. List files to understand project structure
ls -la

# 3. Read the project specification to understand what you're building
cat ./.aidd/spec.txt

# 4. Read the feature list to see all work
cat ./.aidd/feature_list.json | head -50

# 5. Read progress notes from previous sessions
cat ./.aidd/claude-progress.txt

# 6. Check recent git history
git log --oneline -20

# 7. Count remaining tests
cat ./.aidd/feature_list.json | grep '"passes": false' | wc -l
```

Understanding the `/.aidd/spec.txt` is critical - it contains the full requirements
for the application you're building.

### STEP 2: START SERVERS (IF NOT RUNNING)

If `/.aidd/init.sh` exists, run it:
```bash
chmod +x ./.aidd/init.sh
./.aidd/init.sh
```

Otherwise, start servers manually and document the process.

### STEP 3: VERIFICATION TEST (CRITICAL!)

**MANDATORY BEFORE NEW WORK:**

The previous session may have introduced bugs. Before implementing anything
new, you MUST run verification tests.

Run 1-2 of the feature tests marked as `"passes": true` that are most core to the app's functionality to verify they still work.
For example, if this were a chat app, you should perform a test that logs into the app, sends a message, and gets a response.

**If you find ANY issues (functional or visual):**
- Mark that feature as "passes": false immediately
- Add issues to a list
- Fix all issues BEFORE moving to new features
- This includes UI bugs like:
  * White-on-white text or poor contrast
  * Random characters displayed
  * Incorrect timestamps
  * Layout issues or overflow
  * Buttons too close together
  * Missing hover states
  * Console errors

### STEP 4: CHOOSE ONE FEATURE TO IMPLEMENT

Look at /.aidd/feature_list.json and find the highest-priority feature with `"passes": false`.

**Priority Order:**
1. Features with `"priority": "critical"` first
2. Then `"priority": "high"`
3. Then `"priority": "medium"`
4. Finally `"priority": "low"`

Within each priority level, prefer features with `"status": "open"` over `"status": "deferred"`.

Before starting work, update the feature's status to `"in_progress"`:
```json
"status": "in_progress"
```

Focus on completing one feature perfectly and completing its testing steps in this session before moving on to other features.
It's ok if you only complete one feature in this session, as there will be more sessions later that continue to make progress.

### STEP 5: IMPLEMENT THE FEATURE

Implement the chosen feature thoroughly:
1. Write the code (frontend and/or backend as needed)
2. Test manually using browser automation (see Step 6)
3. Fix any issues discovered
4. Verify the feature works end-to-end

### STEP 6: VERIFY WITH BROWSER AUTOMATION

**CRITICAL:** You MUST verify features through the actual UI.

Use browser automation tools:
- Navigate to the app in a real browser
- Interact like a human user (click, type, scroll)
- Take screenshots at each step
- Verify both functionality AND visual appearance

**DO:**
- Test through the UI with clicks and keyboard input
- Take screenshots to verify visual appearance
- Check for console errors in browser
- Verify complete user workflows end-to-end

**DON'T:**
- Only test with curl commands (backend testing alone is insufficient)
- Use JavaScript evaluation to bypass UI (no shortcuts)
- Skip visual verification
- Mark tests passing without thorough verification

### STEP 7: UPDATE /.aidd/feature_list.json (CAREFULLY!)

**YOU CAN ONLY MODIFY THESE FIELDS:**

After thorough verification, update the feature:
```json
"passes": true,
"status": "resolved",
"closed_at": "2025-01-15"
```

Set `closed_at` to today's date when marking a feature as resolved.

**ALLOWED FIELD CHANGES:**
- `"passes"`: `false` → `true` (after verification)
- `"status"`: `"open"` → `"in_progress"` → `"resolved"` (or `"deferred"` if blocked)
- `"closed_at"`: `null` → today's date (when resolved)

**NEVER:**
- Remove tests
- Edit test descriptions
- Modify test steps
- Combine or consolidate tests
- Reorder tests
- Change `area`, `category`, `priority`, or `created_at` fields

**ONLY CHANGE "passes" FIELD AFTER VERIFICATION WITH SCREENSHOTS.**

### STEP 8: COMMIT YOUR PROGRESS

Make a descriptive git commit:
```bash
git add .
git commit -m "Implement [feature name] - verified end-to-end

- Added [specific changes]
- Tested with browser automation
- Updated /.aidd/feature_list.json: marked test #X as passing
- Screenshots in verification/ directory
"
```

### STEP 9: UPDATE PROGRESS NOTES

Update `/.aidd/claude-progress.txt` with:
- What you accomplished this session
- Which test(s) you completed
- Any issues discovered or fixed
- What should be worked on next
- Current completion status (e.g., "45/200 tests passing")

### STEP 10: END SESSION CLEANLY

Before context fills up:
1. Commit all working code
2. Update /.aidd/claude-progress.txt
3. Update /.aidd/feature_list.json if tests verified
4. Ensure no uncommitted changes
5. Leave app in working state (no broken features)

---

## TESTING REQUIREMENTS

**ALL testing must use browser automation tools.**

Available tools:
- puppeteer_navigate - Start browser and go to URL
- puppeteer_screenshot - Capture screenshot
- puppeteer_click - Click elements
- puppeteer_fill - Fill form inputs
- puppeteer_evaluate - Execute JavaScript (use sparingly, only for debugging)

Test like a human user with mouse and keyboard. Don't take shortcuts by using JavaScript evaluation.
Don't use the puppeteer "active tab" tool.

---

## IMPORTANT REMINDERS

**Your Goal:** Production-quality application with all 200+ tests passing

**This Session's Goal:** Complete at least one feature perfectly

**Priority:** Fix broken tests before implementing new features

**Quality Bar:**
- Zero console errors
- Polished UI matching the design specified in /.aidd/spec.txt
- All features work end-to-end through the UI
- Fast, responsive, professional

**You have unlimited time.** Take as long as needed to get it right. The most important thing is that you
leave the code base in a clean state before terminating the session (Step 10).

---

Begin by running Step 1 (Get Your Bearings).
