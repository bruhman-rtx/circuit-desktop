---
name: refute
description: Adversarially attack one or more claimed bugs to see whether they survive scrutiny, without executing anything. Use when the user says "is this real", "refute this", "poke holes in this", or hands over a bug claim from any source - a review tool, a colleague, an issue tracker, or their own suspicion. Read-only and fast.
---

# /refute — attack a claim

You take one or more claimed bugs and try to destroy them. Nothing is executed; this is pure reading, and it is fast.

Use this when the question is *"is this actually a bug?"* rather than *"what bugs are there?"*.

## Read first

`${CLAUDE_SKILL_DIR}/../deep-review/support/contracts.md` §1 and §3.1.

## Phase 0 — Normalize

Take the claim(s) from `$ARGUMENTS` or from the conversation. Convert each to a finding record per `contracts.md` §1.

If a claim has no file/line, locate it in the code yourself before proceeding — a refuter cannot attack an unlocated claim. If you genuinely cannot locate it, say so and ask for a pointer rather than guessing at what the claim refers to.

A claim stated in plain English by the user is a perfectly valid input. Transcribe it into `claim` verbatim rather than reinterpreting it.

## Phase 1 — Attack

Launch one `dr-refuter` per claim, all in a single message, up to 12 concurrent.

## Phase 2 — Report

No `ReportFindings` call — this is a conversational tool. Report as a compact table:

| # | Claim | Verdict | Basis |
|---|---|---|---|
| 1 | resolveTags drops hyphenated tags | **SURVIVES** | No upstream validation found; mobile call path unchecked |
| 2 | Null deref in formatDate | **REFUTED** | Guarded at `src/lib/date.ts:14` — early return on falsy |

Then, for anything that survived, state in one or two sentences what would settle it — and offer `/reproduce <n>` if the answer is "run it."

Carry two things forward honestly:

- **`unverified_assumptions`.** Where the refuter had to take something on faith, say so. A `SURVIVES` resting on an unchecked assumption is weaker than one where everything was verified, and the user needs to see that difference.
- **`NEEDS_EXECUTION`.** This means reading genuinely cannot settle it — report it as an open question, not as a weak survival.

Do not compute a confidence score here. Confidence requires the full pipeline's evidence levels; a number derived from one refutation pass would be false precision.
