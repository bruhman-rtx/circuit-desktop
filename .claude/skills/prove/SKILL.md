---
name: prove
description: Take code-review findings that already exist in this conversation - from /code-review, /security-review, a colleague, or your own analysis - and adversarially verify each one, executing code where possible to prove or disprove it. Use when the user says "prove these", "verify these findings", "are these real", or after any review has produced a list of claimed bugs. Does not find new bugs; use /deep-review for that.
---

# /prove — ground existing findings in evidence

You take findings that **already exist** and determine which survive scrutiny. You do not hunt for new bugs.

This exists because reviewers — including this one — are biased toward finding something, since finding nothing feels like failing the task. A finding that has survived a dedicated attempt to destroy it, and ideally a command transcript showing it happen, is worth more than ten plausible-sounding ones.

## Read first

- `${CLAUDE_SKILL_DIR}/../deep-review/support/contracts.md` — the data model. Not optional.
- `${CLAUDE_SKILL_DIR}/../deep-review/support/reporting.md` — ranking and output contract.

## Phase 0 — Collect and normalize

Gather the findings from the conversation: a prior `/code-review` or `/security-review` result, a pasted PR comment, a colleague's message, or an explicit list from the user. If a `$ARGUMENTS` target is given, prefer it.

Convert each into a finding record per `contracts.md` §1. You are transcribing, not re-deriving:

- Assign `finding_id` sequentially (`F01`, `F02`, …).
- Set `producer` to the actual source: `code-review`, `security-review`, `human`, or `conversation`.
- **Do not invent `cited_lines`.** If the source finding has no file/line, read the code and locate it. If you cannot, keep the finding but mark `coverage_gap: true` — never fabricate a citation to satisfy the schema.
- Set `severity` yourself from the §1 rubric — external sources rarely use a comparable scale.
- `evidence_level: 0`, `state: "DETECTED"`.

If you find zero findings in the conversation, say so and stop. Do not go looking for bugs — that is `/deep-review`.

Print the normalized list before proceeding, so the user can see what is about to be tested.

## Phase 1 — Runbook (parallel with Phase 2)

Launch `dr-runbook-probe` once for the repo. Do not wait on it before starting refutation; join it before Phase 3.

If it fails, assume every file is `PURE` and let the executor's two-strike rule catch the mistake. Never block on the probe.

## Phase 2 — Refute (barrier)

Launch one `dr-refuter` per finding, all in a single message, up to 12 concurrent.

Then:
- `REFUTED` → drop. Record it; refuted findings still go to telemetry.
- `SURVIVES` → L1.
- `NEEDS_EXECUTION` → L1, queued for Phase 3 with priority.

**Print the surviving findings to chat now.** Execution takes minutes; the user should see the shape of the result early.

## Phase 3 — Execute (barrier)

Only for findings whose file class is `PURE`, `UNIT`, or `API`, in an allowlisted repo (`Pair`, `aphelion-tools-site`).

Rank survivors by `severity_weight × confidence` and take the **top 3**. Launch one `dr-repro-engineer` each, ≤3 concurrent, 240s total budget.

Findings on `UI`/`DEVICE`/`BUILD` files, or in non-allowlisted repos, do **not** simply stop. Send each to a second `dr-refuter` framed differently from the first: *"Ignore whether the mechanism is real. Ask only whether any live caller can reach this code path with the offending input."* When you cannot buy evidence, buy scrutiny.

If any executor returns `TOOLING_ERROR`, **stop all execution immediately** — the sandbox is not holding. Report what you have and say so prominently.

Apply the asymmetry rule without exception: `NOT_RUN` and `EXEC_FAILED` never lower a finding's standing.

## Phase 4 — Score and report

1. Compute `confidence` per `contracts.md` §3.3. Look up history first:
   ```
   python ${CLAUDE_SKILL_DIR}/../deep-review/support/telemetry.py history --repo <repo> --hashes <h1,h2,...>
   ```
   Apply the returned `confidence_delta` per finding.
2. Rank per `reporting.md` §1.
3. Call `ReportFindings` once. Write the sidecar to `<scratchpad>/deep-review/evidence.md`.
4. Log to telemetry:
   ```
   echo '<json array of finding records>' | python ${CLAUDE_SKILL_DIR}/../deep-review/support/telemetry.py record --repo <repo>
   ```
   Include refuted findings — detector precision is meaningless without them. Telemetry failure is ignored; it must never affect the run.

## Always report

- How many findings you started with, and how many survived.
- Which stages degraded, if any.
- For each confirmed finding, the one decisive line of real output.

An empty result is a valid and honest outcome. If everything was refuted, say so plainly and name the reasons. Never pad the report to look productive — one manufactured finding destroys the credibility of every real one.
