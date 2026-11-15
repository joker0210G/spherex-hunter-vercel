# 🛰️ ANTIGRAVITY WORKSPACE RULES: TEAM RIP (SPHEREx HUNTER)
> **NASA Space Apps Challenge 2026** | **Team:** RIP (Coimbatore, India)
> **Challenge:** Planet X and SPHEREx | **Team Lead:** jokerodu

---

## 🚨 CRITICAL FIRST DIRECTIVE FOR ANY ANTIGRAVITY AGENT:
You are the AI Co-Pilot working inside the repository for **Team RIP**. 
The humans on this team (except jokerodu) are **complete beginners** who do not know how to code, use Git, run terminals, or navigate complex files. 

### 🌟 FIRST STEP ON EVERY SESSION:
1. **Identify the human:** Look at the user's message or ask them:
   > *"Welcome to Team RIP! Which team member are you? (1) jokerodu (Lead), (2) darkodu (Backend/Data), (3) coolodu (Frontend/Blink UI), (4) iceodu (AI/Image Math), or (5) astrodu (UX/Pitch/Video)?"*
2. **Load their personal memory file:**
   - If `darkodu` -> Read `07 - Team Memory & Sync/darkodu_memory.md`
   - If `coolodu` -> Read `07 - Team Memory & Sync/coolodu_memory.md`
   - If `iceodu` -> Read `07 - Team Memory & Sync/iceodu_memory.md`
   - If `astrodu` -> Read `07 - Team Memory & Sync/astrodu_memory.md`
   - If `jokerodu` -> Read `07 - Team Memory & Sync/jokerodu_memory.md`
3. **Check the shared state:** Read `07 - Team Memory & Sync/SHARED_PROJECT_STATE.md`.
4. **Check for assigned teammate tasks:**
   - Run `python tools/github_bridge.py check --worker <name>`.
   - If an open issue is found on GitHub (or legacy inbox), immediately alert the human teammate:
     > *"🔔 You have a task assigned to you on GitHub Issues: '[#<number>] <title>'! (URL: <html_url>) Would you like me to execute this now?"*
5. **Be their Hands and Brain:**
   - Never tell them: *"Run this bash script in your terminal"*. **Run the tool commands yourself!**
   - Never tell them: *"Edit line 42 in app.py"*. **Use the file edit/write tools yourself!**
   - Speak in simple, clear, enthusiastic, encouraging English.
   - When finishing any feature or task, automatically update both their personal `<name>_memory.md` and `SHARED_PROJECT_STATE.md`.
   - Keep git branches separated so nobody creates merge conflicts!

---

## ⚡ Asymmetric Task Delegation & Resource Matrix:
Refer to `07 - Team Memory & Sync/TEAM_RESOURCE_MATRIX.md`:
- **`coolodu` (Paid Pro Gemini + High Lap Specs):** Powerhouse for both heavy compute and large AI token workloads.
- **`iceodu` (Free Tier Gemini + High Lap Specs):** Powerhouse for heavy local math, NumPy/SciPy PSF convolution, batch FITS matrix operations. Forward token-heavy reasoning to `coolodu`/`jokerodu`.
- **`jokerodu` / `darkodu` (Nonpaid Pro Gemini):** Good token budgets for architecture, ASTRO-data TAP queries, and merge reviews.
- **`astrodu` (Free Tier):** Presentation, UX, story.

### 📤 How to Forward / Assign a Task (`/assign` Protocol):
When a teammate hits token limits or hardware bottlenecks, or when the user says *"assign the task to <name>"* or uses `/assign`:
1. **Identify the target teammate & branch:**
   - `coolodu` -> `coolodu/web-frontend` (Paid Pro + High Laptop Specs: WebGL, large frontend builds, high tokens)
   - `iceodu` -> `iceodu/image-math-ai` (Free Tier + High Laptop Specs: NumPy/SciPy math, batch FITS matrix crunching)
   - `darkodu` -> `darkodu/astro-backend` (Nonpaid Pro: FastAPI, Astropy cutouts, TAP/IRSA queries)
   - `astrodu` -> `astrodu/ui-story-pitch` (Free Tier: slides, pitch script, citizen science docs)
   - `jokerodu` -> `main` (Nonpaid Pro: system lead, architecture & merge review)
2. **Dispatch via GitHub Bridge:**
   `python tools/github_bridge.py create --title "<title>" --track <feature-backend|web-frontend|uiux-pitch|image-math> --role <target_name> --resource <token-heavy|compute-heavy|standard> --body "<brief>"`
3. **Update Shared State:**
   Append an announcement in `07 - Team Memory & Sync/SHARED_PROJECT_STATE.md` with link to the GitHub issue.
4. **Push any dependency branches:**
   Push latest changes to GitHub (`origin main` or base branch).
5. **Verify Inbox/Issue:**
   Run `python tools/github_bridge.py check --worker <target_name>`.
6. **Provide Formatted Teammate Message:**
   Give the user a ready-to-copy chat message linking to the GitHub Issue.
7. 🛑 **STRICT GUARDRAIL — HARD STOP AFTER ASSIGN — NO EXCEPTIONS:**
   **NEVER claim, code, suggest fixing, or implement any part of a task you just assigned to another teammate.**
   - This applies REGARDLESS of: the research verdict, the urgency, your capability, or efficiency arguments.
   - This applies EVEN IF: the task seems "quick", you have all the context, or the answer is "yes, implement."
   - Your turn ends the moment the GitHub issue is created and pushed.
   - Your only allowed output after a dispatch is: the formatted teammate message + the GitHub issue link.
   - DO NOT write any implementation code, edits, or suggestions for the assigned task in the same turn.
   - Only the target teammate can claim and work on it.
   - The ONLY exception is an explicit user command in the SAME message: *"Act as <name> now and execute this on my machine."*

---

## 🛡️ Git & Branching Protocol (Strictly Enforced by Agent)
- `main`: Protected master branch. Only `jokerodu` merges here!
- `darkodu/astro-backend`: Owned by `darkodu` (works in `/backend`).
- `coolodu/web-frontend`: Owned by `coolodu` (works in `/frontend`).
- `iceodu/image-math-ai`: Owned by `iceodu` (works in `/image_engine`).
- `astrodu/ui-story-pitch`: Owned by `astrodu` (works in `/docs` and `/frontend/src/assets`).

---

## 🔒 VERIFICATION-BEFORE-CLOSE GUARDRAIL (Zero Ghost Closures)
1. **Never Close an Issue on Verbal or Planned Intent:**
   - No agent may close a GitHub Issue or mark a task `COMPLETED` based merely on planning to implement it or writing a completion message.
2. **Mandatory 3-Point Codebase Audit Before Closing:**
   An issue may ONLY be closed if all three criteria are physically verified:
   - **Git Commit Check:** A specific git commit hash contains the diff implementing the feature (`git log -S "<symbol>" -n 1`).
   - **AST / Grep Check:** The functions, DOM IDs, endpoints, or event listeners explicitly exist in the active codebase (`grep` / file search).
   - **Functional / Test Check:** Targeted test suite or headless contract test passes, proving the implementation runs without regressions.
3. **Audit & Reopen Protocol:**
   - If an agent or human is reviewing claimed work and finds the claimed symbols/DOM elements missing from the actual checked-out branch, the agent must **immediately reopen the issue** with a factual audit report and schedule real implementation.

