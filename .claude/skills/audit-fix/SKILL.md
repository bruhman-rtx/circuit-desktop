---
name: audit-fix
description: Review a fix against the bug it was meant to solve - does it fully fix it, what did it break, and does the repro now pass. Use after applying any bug fix, whether written by hand or by /deep-review --fix, and when the user says "check this fix", "did that actually fix it", or "review the patch".
---

# /audit-fix — review the fix, not just the bug

`$ARGUMENTS`: optional finding reference or path.

You review a fix against the specific problem it claims to solve.

This closes the loop that almost every review workflow leaves open: a reviewer flags an issue, the author patches it under pressure to satisfy a critic, and **that patch ships unreviewed**. The fix typically gets less scrutiny than the code that caused the bug, despite being written faster and with a worse incentive.

## Read first

`${CLAUDE_SKILL_DIR}/../deep-review/support/contracts.md` — especially §3.2 for repro artifacts.

## Phase 0 — Pair each fix with its finding

Establish two things. Without both, this skill cannot do its job.

**The fix diff.** Usually `git diff HEAD`, or the changes since the review ran. If the fix is already committed, `git diff HEAD~1` or the relevant range.

**The original finding.** From `/deep-review` or `/prove` earlier in this session, from `<scratchpad>/deep-review/run-state.json`, or from the user's description.

If you cannot identify what problem a change was meant to solve, say so and ask. Auditing a patch against a guessed intent produces confident nonsense — you would be inventing the standard you then grade against.

Also recover any **repro artifact** for the finding, from `run-state.json` under `execution.artifacts`.

## Phase 1 — Audit

Launch one `dr-patch-auditor` per (finding, fix) pair, in a single message, up to 12 concurrent.

## Phase 2 — Re-run the repro

For every finding with a retained artifact, re-run it **unchanged**, exactly as `dr-repro-engineer` originally ran it — same command, same cwd.

```
$ node_modules/.bin/tsx <scratch>/repro/F03/repro.ts
```

| Result | Meaning |
|---|---|
| Was failing, now passes | Strong evidence the fix works |
| Still fails | The fix does **not** work, whatever the diff looks like |
| Errors differently | Neither — investigate; the fix may have moved the failure |

This is nearly free, since the script already exists, and it is the single most reliable signal available here.

**But it is not sufficient on its own.** A fix that special-cased the exact input the repro used will pass while the bug remains. That is precisely what the auditor's reasoning catches, so weigh both — a passing repro with a `PARTIALLY_FIXED` audit means the audit is probably right.

If the repro cannot be re-run (artifact deleted, worktree gone), say so. Do not treat an un-runnable repro as a pass.

## Phase 3 — Report

Per fix:

| Finding | Audit | Repro | Verdict |
|---|---|---|---|
| F03 hyphenated tags dropped | PARTIALLY_FIXED | ✓ passes | **Not done** — second call site at `search.ts:142` untouched |

Then, in order:

1. **Regressions the fix introduced**, with citations. These are new bugs and should be treated as such — they are often more serious than the original, because they are newer and less examined.
2. **Residual risk** — what the fix left behind.
3. **Scope creep** — substantial unrelated changes riding along with the fix.

If findings came from `ReportFindings` earlier this session, re-call it with `outcome` per finding: `fixed`, `no_change_needed`, or `skipped`.

> A fix that does not flip its own repro from failing to passing is not `fixed`. If the audit says `PARTIALLY_FIXED` or `NOT_FIXED`, the honest outcome is `skipped` with the reason — not `fixed` because a patch was applied.

Report `NOT_A_BUG_ANYWAY` prominently when it comes up. It means the code was changed for no reason, and reverting is usually the right call — carrying an unnecessary change is a real cost that nobody notices later.
