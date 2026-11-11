---
name: deep-review
description: Hunt for bugs in a diff using parallel detectors with distinct lenses, then adversarially refute each candidate and execute code to prove the survivors. Use when the user asks for a thorough or deep code review, wants bugs found and verified rather than just listed, or says "review this properly". Bug hunting only - for style, reuse, and simplification cleanups use /simplify instead.
---

# /deep-review — find, refute, prove

`$ARGUMENTS`: `[--quick|--deep] [--fix] [--paths <glob>] [--spec "<text>"|<path>]`

You find bugs with parallel detectors, then try to destroy each one, then run code to prove what survives. Most findings from any reviewer are wrong; the pipeline exists to separate the few that are not.

**Scope: bugs only.** Reuse, simplification, efficiency, and altitude cleanups belong to `/simplify` — do not duplicate it.

## Read first

All three, before Phase 0:
- `${CLAUDE_SKILL_DIR}/support/contracts.md` — data model
- `${CLAUDE_SKILL_DIR}/support/intake.md` — diff gathering, sharding, dedup, resilience
- `${CLAUDE_SKILL_DIR}/support/reporting.md` — ranking and output

## Phase 0 — Intake (inline, no agents)

Follow `intake.md` §1–§3 exactly.

1. Gather the diff. **Uncommitted work first** — these repos usually sit on `main` with an empty range diff.
2. Apply exclusions. Count what you dropped.
3. Bucket by size; pick the detector set per `intake.md` §2. **XL refuses** — ask for `--paths`.
4. Build the intent brief per `intake.md` §3. **If it would be empty, do not launch `dr-intent-conformance`** — note the skip for the report.
5. Write initial run state to `<scratchpad>/deep-review/run-state.json`.

Tell the user what you are about to do in one line: bucket, detector count, whether the intent lens is active.

## Phase 1 — Runbook + detect

Launch `dr-runbook-probe` **and** all selected detectors **in a single message** so they run concurrently. The probe is not a barrier — join it before Phase 3.

Give every detector: the diff (its shard), the complete changed-file index, and the repo root. Give `dr-intent-conformance` the brief; give `dr-pitfall-specialist` the stack once the probe returns, or the stack you can infer from `package.json` if it has not.

`--quick` stops after this phase plus dedup. No refutation, no execution — roughly built-in cost, and the right choice for a small diff.

## Phase 2 — Dedup and rank (inline, no agents)

Per `intake.md` §4: merge on `(file, line±5, same mechanism)`, drop findings with empty `cited_lines`, rank, **cap at 12**.

Look up history and apply the modifier:
```
python ${CLAUDE_SKILL_DIR}/support/telemetry.py history --repo <repo> --hashes <h1,h2,...>
```

## Phase 3 — Refute (barrier)

One `dr-refuter` per surviving finding, single message, ≤12 concurrent.

`REFUTED` → drop (still logged). `SURVIVES` → L1. `NEEDS_EXECUTION` → L1, priority for Phase 4.

**Print the survivors to chat now**, before execution. The user should see the result shape at ~2 minutes rather than ~6.

## Phase 4 — Execute (barrier)

Rank survivors and take the **top 3**. Launch `dr-repro-engineer` for those whose file class is `PURE`/`UNIT`/`API` in an allowlisted repo (`Pair`, `aphelion-tools-site`). ≤3 concurrent, 240s total.

Everything not executed — wrong class, wrong repo, or below the cap — goes to a second `dr-refuter` framed on reachability: *"Ignore whether the mechanism is real. Can any live caller reach this path with the offending input?"* When you cannot buy evidence, buy scrutiny.

`--deep` additionally sends every L3 finding to a reachability refuter, and raises the detector shard count.

**On `TOOLING_ERROR`: stop all execution immediately.** The sandbox is not holding. Report loudly with both git-status captures.

Asymmetry rule, without exception: `NOT_RUN` and `EXEC_FAILED` never lower a finding.

## Phase 5 — Report

1. Compute `confidence` per `contracts.md` §3.3 — **derived, never authored**. Every value must be reconstructable by hand from the table.
2. Rank per `reporting.md` §1.
3. Call `ReportFindings` once. Sidecar to `<scratchpad>/deep-review/evidence.md`.
4. Log every finding, including refuted ones, to telemetry. Detector precision is meaningless without the refuted set.

Close with the degradation notice: stages that failed, findings dropped by the cap, files excluded, and whether the intent lens was skipped. **A review that reports fewer findings must never look like a review that found nothing.**

## Phase 6 — `--fix` only

For each finding, in rank order:

1. Apply the fix. Skip anything that would change intended behavior, needs changes well outside the diff, or that you judge a false positive — note the skip rather than arguing with it.
2. Launch `dr-patch-auditor` on the fix diff, with the finding it claims to fix.
3. **Re-run the retained repro artifact.** It must now pass. A fix that does not flip its own repro from failing to passing is not `fixed` — it is `skipped`, and say why.
4. Re-call `ReportFindings` with `outcome` per finding.

## Cost

`--quick` detectors only · default 4 detectors + refute all + execute 3 · `--deep` more shards, execute up to 8, second refutation round.

Execution is the expensive stage and is capped hard. Refutation is not, because pre-refutation severity is a detector's own unverified guess — letting it gatekeep scrutiny would defeat the purpose of having a refuter at all.
