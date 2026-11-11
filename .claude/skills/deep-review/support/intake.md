# deep-review shared intake

Diff gathering, normalization, sharding, dedup, and resilience. Read alongside `contracts.md`.

---

## 1. Gather the diff

**Order is inverted relative to the built-in `/code-review`, deliberately.** These repos frequently sit directly on `main`/`master`, where the range diff is empty and all the real work is uncommitted.

```sh
git rev-parse --show-toplevel                  # repo root; bail if this fails
git status --porcelain=v1 -uall                # untracked files matter
git diff HEAD                                  # (1) uncommitted  -> provenance: "uncommitted"
git diff @{upstream}...HEAD                    # (2) committed    -> provenance: "committed"
git diff main...HEAD  ||  git diff master...HEAD   # (3) fallback, no upstream
git diff HEAD~1                                # (4) last resort
```

Take (1) always. Then take the first of (2)/(3)/(4) that returns a non-empty diff. Union them, keeping the `provenance` label per hunk — refuters weigh in-flight work differently from shipped work.

ResourceLibrary and pair-mobile have **no upstream**; the ladder handles that silently. Never assume `@{upstream}` resolves.

If an explicit target is passed (`--paths`, a branch, a path), review that instead and skip the ladder.

### Exclusions

Drop these hunks before counting size or sharding. Without this, Loom (51 dirty) and DailyManager (55 dirty) flood the diff with noise:

```
*.lock  *-lock.yaml  package-lock.json  pnpm-lock.yaml  yarn.lock
dist/  build/  dist-electron/  dist-pkg/  out/  .next/  node_modules/  __pycache__/  .venv/
prisma/migrations/  *.min.*  *.generated.*  *.snap
*.png *.jpg *.jpeg *.gif *.svg *.ico *.pdf *.pptx *.apk *.ipa *.woff *.woff2 *.ttf
```

State the exclusion count in the report. Silent truncation reads as "covered everything" when it didn't.

---

## 2. Size buckets and detector selection

| Bucket | Threshold | Detectors launched |
|---|---|---|
| XS | <50 changed lines **or** <3 files | `behavior-delta`, `intent-conformance` — and force `--quick` |
| S | <300 lines | all 4, unsharded |
| M | <1500 lines | all 4, sharded to ≤8 tasks |
| L | <5000 lines **or** <100 files | all 4, directory-sharded to ≤12 tasks |
| XL | above that | **refuse.** Ask for `--paths <glob>` and stop. |

Never exceed **12** concurrent agent tasks (machine cap is 14; leave headroom).

**Shard by directory or module, never by arbitrary file count** — `dr-contract-tracer` is useless on an incoherent slice. Every shard receives the *complete* changed-file index (paths only, no content) so it knows what else moved.

---

## 3. The intent brief

Written by the **orchestrator**, not an agent — only the main thread has the conversation.

Assemble from, in order of preference:
1. `--spec "<text>"` or `--spec <path>` if passed.
2. The user's original request in this session, plus any correction they issued mid-task.
3. Nothing.

> **Hard rule:** if the brief would be empty, **do not launch `dr-intent-conformance`.** In a fresh session it will reconstruct a "spec" from commit messages and grade the diff against its own invention — a pure hallucination generator. Skip it and say so in the report.

A brief is a paragraph of what was asked for, including anything explicitly ruled out. It is not the diff, and it must not be derived from the diff.

---

## 4. Dedup

Runs inline in the orchestrator after detection. No agent call — this is string and location work.

Merge two findings when **all** hold:
- same `file`
- `line` within ±5
- claims describe the same mechanism (not merely the same symptom)

On merge: keep the higher `severity`, keep the earlier `finding_id`, union `cited_lines`, record both producers, and apply the +0.05 independent-corroboration modifier.

Then:
- Drop any finding with empty `cited_lines` — it is an assertion, not a finding.
- Rank by the §5 formula in `reporting.md`.
- **Cap at 12** entering refutation.

Everything downstream is per-finding fan-out, so this cap sets the cost of the run. Log how many were dropped by the cap.

---

## 5. Stage gates

| Stage | Concurrency | Barrier? | Cap |
|---|---|---|---|
| Runbook probe | 1 | no — runs alongside detection, joined before execution | — |
| Detect | ≤12 | yes | per size bucket |
| Refute | ≤12 | yes | all 12 findings |
| Execute | ≤6 | yes | **top 3 survivors**, 240s total |
| Report | 1 | — | — |

**Print surviving findings to chat immediately after refutation.** Execution adds minutes; the user should see value at ~2 minutes rather than ~6. A slow tool gets abandoned regardless of how good its output is.

Execution is capped at 3 because it is the expensive stage. Refutation is not cut, because pre-refutation severity is a detector's own unverified guess — the least reliable signal in the system — and letting it gatekeep scrutiny defeats the point.

---

## 6. Resilience

Every stage degrades; no stage aborts the run. A subagent that dies returns null — filter and continue.

| Failure | Behavior |
|---|---|
| Detector fails or returns non-conforming JSON | Continue with the others. Record `detector_failed` in telemetry. Name it in the report. |
| Runbook probe fails | Assume every file is `PURE` and let the two-strike rule catch it. Never block detection on the probe. |
| Refuter fails | Finding stays `SURVIVED` at L0 with the −0.05 modifier. Never silently dropped. |
| Executor fails | `EXEC_FAILED`; report at pre-execution level (asymmetry rule). |
| Executor returns `TOOLING_ERROR` | **Stop all execution for the run.** A dirty-tree invariant breach means the sandbox is not holding; do not launch more executors. |
| `ReportFindings` unavailable | Markdown fallback in `reporting.md`. |
| Telemetry write fails | Ignore. Telemetry must never affect a run's outcome. |

> **A review that reports fewer findings must never look like a review that found nothing.** Every report ends with a line naming which stages degraded, or stating that none did.
