---
name: reproduce
description: Prove or disprove a single suspected bug by actually running code - writing a minimal repro script in a sandbox, executing it, and checking whether a real caller can reach the failing path. Use when the user says "reproduce this", "prove it runs", "does this actually happen", or wants a claimed bug demonstrated rather than argued. Writes only to git-ignored paths and never touches the working tree.
---

# /reproduce — demonstrate one bug

You take a **single** suspected bug and try to make it happen for real, with a command transcript to show for it.

This is the debugging entry point for the execution machinery, and the tool to reach for when an argument about whether something is a bug has gone in circles. Running it settles it.

## Read first

- `${CLAUDE_SKILL_DIR}/../deep-review/support/contracts.md` — especially §3.2 and §5.

## Phase 0 — Locate and normalize

Take the target from `$ARGUMENTS`, or from the conversation if the user said "reproduce that."

Build one finding record per `contracts.md` §1. You must have `file`, `line`, and a concrete `claim` before proceeding — the executor needs a specific thing to test. If any is missing, find it in the code; if you cannot, ask rather than guessing.

## Phase 1 — Runbook

Launch `dr-runbook-probe` for the repo. Wait for it — unlike `/prove`, there is nothing else to overlap with, and the executor's strategy depends entirely on the file's execution class.

If the class is `UI`, `DEVICE`, or `BUILD`, stop before spending an agent. Tell the user this file cannot be executed in isolation and why, then offer `/refute` as the alternative — scrutiny is what's available when evidence isn't.

If the repo is not `Pair` or `aphelion-tools-site`, stop and say so. The execution allowlist exists because these repos carry 12–55 uncommitted files and the sandbox has not yet been proven against them. Offer `/refute` instead, and mention the allowlist is a one-line edit in `dr-repro-engineer.md` when the user is ready to widen it.

## Phase 2 — Execute

Launch one `dr-repro-engineer` with the finding and the runbook. Give it the full per-class budget — 30s `PURE`, 60s `UNIT`, 90s `API` — since it is the only thing running.

If the finding claims a **regression**, say so explicitly in the prompt. That is what triggers tier-1 differential mode, where the same probe runs against both old and new code. Two different outputs from one probe is the strongest evidence this system produces.

## Phase 3 — Report

Show the actual transcript. This skill's entire value is the real output:

```
$ node_modules/.bin/tsx <scratch>/repro/F01/repro.ts     (exit 1, 1.8s)
AssertionError: expected 2 tokens for 'ui-kit', got 1
```

Then state, in order:

1. **The verdict** and what it means — `REPRODUCED` (with reachability) is proof; `PARTIAL` means the mechanism was shown on a simplified copy; `REFUTED_BY_EXECUTION` means you ran it and the code was correct, which is just as valuable a result.
2. **Reachability** — the caller and how it produces the input. If the executor could not find a reachable caller, say so prominently. Reproducing a failure from inputs no caller can supply is not evidence of a bug, and presenting it as one would be worse than never running anything.
3. **The differential**, if tier 1 ran — old output vs new.
4. **Where the artifact lives.** Keep it; if the bug gets fixed, re-running that exact script is what proves the fix works.

If the verdict is `NOT_RUN` or `EXEC_FAILED`, report what blocked it and at which rung of the ladder. Never let that read as "not a bug" — it means the environment did not permit evidence, which says nothing about the code.

If the verdict is `TOOLING_ERROR`, surface it loudly with both git-status captures. That means the sandbox invariant broke, and no further execution should run until it is understood.
