<!-- claude-setup:begin -->
# Neil's global instructions (cloud copy)

Built from the laptop's `~/.claude/CLAUDE.md` and its @-includes, inlined because `@~/...` includes do not resolve inside a repo.
Included: RTK.md, ROUTING.md, BUILDS.md, ANSWERS.md. Left out on purpose: WORKFLOW-LOGS.md (it writes to a local Obsidian vault that does not exist in the cloud).
The `scout` and `hand` agents that ROUTING.md names come from the `neil-setup` plugin, or from `.claude/agents/` if you copied them into the repo.

---

<!-- from ~/.claude/RTK.md -->

# RTK - Rust Token Killer

**Usage**: Token-optimized CLI proxy (cuts up to 90% of bash output)

## Meta Commands (always use rtk directly)

```bash
rtk gain              # Show token savings analytics
rtk gain --history    # Show command usage history with savings
rtk discover          # Analyze Claude Code history for missed opportunities
rtk proxy <cmd>       # Execute raw command without filtering (for debugging)
```

## Installation Verification

```bash
rtk --version         # Should show: rtk X.Y.Z
rtk gain              # Should work (not "command not found")
which rtk             # Verify correct binary
```

⚠️ **Name collision**: If `rtk gain` fails, you may have reachingforthejack/rtk (Rust Type Kit) installed instead.

## Hook-Based Usage

All other commands are automatically rewritten by the Claude Code hook.
Example: `git status` → `rtk git status` (transparent, 0 tokens overhead)

Refer to CLAUDE.md for full command reference.

---

<!-- from ~/.claude/ROUTING.md -->

# Model & effort routing

Session baseline is `opus[1m]` at the configured effort. Do not change the main
thread's model mid-session — it would drop the 1M context window. Route instead:

**Delegate the cheap work** (this is where model switching happens; subagents get
fresh context, so a small model is safe there):
- "Where does X live?" / "which files touch Y?" → `scout` (Haiku). Never grep the
  whole repo from the main thread when you only need the location.
- Fully-decided mechanical work — boilerplate, the same edit across many files,
  tests for existing behaviour → `hand` (Sonnet). Decide on the main thread, hand
  over the typing.

**Let effort follow the task** (main thread, model unchanged):
- Hard: unknown-cause debugging, architecture, concurrency, security, migrations,
  a bug that survived a fix → `think-max`.
- Trivial and fully specified: typo, rename, version bump, a fact from a file
  already read → `think-light`.

**Never downshift** correctness-critical work: reviews, security, anything
touching data integrity, or a decision that is expensive to reverse. When unsure
which tier applies, stay on the main thread at normal effort — a wrong answer
cheaply is worse than a right answer at cost.

A subagent's report is a claim, not a fact. Spot-check anything load-bearing.

---

<!-- from ~/.claude/BUILDS.md -->

# Mobile build policy

Applies to every project with a native mobile target (Expo, React Native, Flutter,
bare Android/iOS).

## Android — local only, always

Android builds MUST be run locally on this machine. Never use EAS Build, any other
cloud build service, or a remote CI runner to produce an Android artifact.

- Use `./gradlew assembleRelease` / `assembleDebug` / `bundleRelease` (or the
  Expo local equivalent: `npx expo run:android`, `eas build --platform android --local`).
- Remember the JDK rule: Bash gets JVM 8, so export Android Studio's bundled JBR
  before invoking `./gradlew`.
- If a local Android build fails, fix it locally. Falling back to a cloud build is
  not an option — report the failure instead.

## iOS — EAS, but only after explicit confirmation

iOS builds are done on EAS (no macOS here, so local is not possible). But an EAS
iOS build is never started on my own initiative:

- Ask first, in plain terms: which profile, which bundle id / EAS project, and
  whether it consumes a build credit.
- Wait for an explicit "yes, build it" from Neil. Silence, an earlier approval of a
  different build, or a general "ship it" is NOT confirmation.
- One confirmation covers one build. Re-ask for the next one.
- Never run `eas build --platform ios` (or `--platform all`, which includes iOS)
  without that confirmation.

`--platform all` counts as an iOS build AND violates the Android rule — never use it.

---

<!-- from ~/.claude/ANSWERS.md -->

# Reading Neil's answers

When a reply of mine contains more than one question and Neil answers without
saying which question he's answering, resolve the ambiguity by the length of the
message he was replying to:

- **Under ~500 words** → he is answering the **first (topmost)** question. Short
  replies get read top-down, so the first question is the one in mind.
- **Over ~500 words** → he is answering the **last (bottommost)** question. On long
  replies the closest question to the end is the one still on screen.

This holds regardless of where the questions sit among the prose — a response split
into [text, question, text, text, question] still resolves to the first question if
short, the last if long.

Corollaries:

- Ambiguity is my problem, not his. Don't ask "which question do you mean?" as a
  reflex — apply the rule and proceed.
- Only confirm when acting on the wrong reading would be costly or hard to undo. Do
  it in one line, and act on the rule's default while asking where that's safe.
- Prevention beats interpretation: prefer asking ONE question per response. If
  several are genuinely needed, use AskUserQuestion so each answer is bound to its
  question, or number them and ask him to reply with the number.
- An answer whose content only fits one of the questions overrides the rule — match
  on meaning first, fall back to position.
<!-- claude-setup:end -->
