# deep-review shared contracts

Read by every `dr-*` agent and every deep-review skill. This is the data model; nothing here is optional.

---

## 1. The finding record

Every agent emits **exactly one fenced ```json block** containing either a single finding record or an array of them. No prose before or after the block — anything outside it is discarded.

```json
{
  "finding_id": "F03",
  "producer": "dr-behavior-delta",
  "file": "src/api/search.ts",
  "line": 88,
  "symbol": "resolveTags",
  "severity": "HIGH",
  "category": "correctness",
  "claim": "resolveTags drops tags whose name contains a hyphen",
  "mechanism": "The new split on /[\\s,]+/ replaced a split on /[\\s,-]+/, so 'ui-kit' now yields one token instead of two, and the lookup on line 94 misses.",
  "cited_lines": ["src/api/search.ts:88-94", "src/lib/tags.ts:12"],
  "evidence_level": 0,
  "state": "DETECTED",
  "next_stage": "REFUTE"
}
```

### Field rules

| Field | Rule |
|---|---|
| `finding_id` | `F` + zero-padded ordinal, assigned by the orchestrator. Agents receiving a finding echo it back unchanged. |
| `producer` | The agent name that first emitted it. Never rewritten downstream. |
| `file` | Repo-relative, forward slashes. Never absolute. |
| `line` | Integer, 1-indexed, the line the defect anchors to. |
| `symbol` | Enclosing function/class/component name, or `null` at module scope. Used for `finding_hash`. |
| `severity` | `CRITICAL` \| `HIGH` \| `MEDIUM` \| `LOW`. Set **once**, by the detector, from the rubric below. |
| `category` | kebab-case slug, ≤40 chars. `correctness`, `contract-break`, `intent-drift`, `silent-failure`, `security`, `data-loss`. |
| `claim` | One sentence. The defect only — no rationale, no consequence clause. |
| `mechanism` | 2–3 sentences. Why it fails. |
| `cited_lines` | Array of `path:line` or `path:start-end`. **Every claim must cite at least one.** A finding with an empty `cited_lines` is invalid and is dropped at dedup. |
| `evidence_level` | Integer 0–4. See §2. Agents set only their own stage's level; they never raise it beyond what they earned. |
| `state` | See §4. |
| `next_stage` | `REFUTE` \| `EXECUTE` \| `REPORT` \| `DROP`. The producer's recommendation; the orchestrator may override. |

**Severity is set once.** Downstream stages append fields and advance `state`. They never rewrite `claim` or `severity`. This is deliberate: a refuter or executor that could raise severity would inflate it to justify the work it just did.

### Severity rubric

| | Meaning |
|---|---|
| `CRITICAL` | Data loss, data corruption, auth bypass, or silent production of wrong results that a user would act on. |
| `HIGH` | Crash, hang, or wrong behavior on an input a normal user can supply. |
| `MEDIUM` | Wrong behavior on an edge case, or a contract break that only breaks a non-obvious consumer. |
| `LOW` | Degraded behavior with an obvious symptom, or a break only reachable from test/dev code. |

If a finding does not clear `LOW`, do not emit it. Style, naming, and preference belong to `/simplify`, not here.

### finding_hash

```
finding_hash = sha256(file + "\0" + symbol + "\0" + normalize(claim))[:16]
normalize(s) = lowercase, collapse whitespace, strip trailing punctuation
```

**Excludes `line`** — line numbers shift with unrelated edits, and history (§6 of the plan) must survive code movement.

---

## 2. Evidence levels

| Level | Name | Earned by |
|---|---|---|
| **L0** | Detected | A detector emitted it with valid `cited_lines`. |
| **L1** | Survived | A refuter tried to destroy it and failed. |
| **L2** | Static proof | Full call chain cited from an entry point to the defect, **and** the violated invariant quoted from source or docs. |
| **L3** | Executed | Code was run and the failure was demonstrated in real output. |
| **L4** | Executed + reachable | L3, **and** a real caller is cited that can produce the triggering input. |

L2 is not "a better argument than L1" — it is a specific artifact: a chain of `file:line` hops plus a quoted invariant. If either half is missing, it stays L1.

**L4 requires the `reachability` block (§3.2).** No exceptions. An agent that authors its own inputs can always break a function; without reachability, execution manufactures confidence rather than earning it.

---

## 3. Appended stage fields

### 3.1 `refutation` — appended by dr-refuter

```json
"refutation": {
  "verdict": "SURVIVES",
  "attempted": "Checked whether callers pre-validate the tag string.",
  "counter_evidence": [],
  "unverified_assumptions": ["Did not read the mobile client's call path."]
}
```

`verdict` ∈ `REFUTED` | `SURVIVES` | `NEEDS_EXECUTION`.

`REFUTED` requires at least one entry in `counter_evidence`, each a `file:line` citation showing the guard, validation, type constraint, or dead path that makes the finding impossible. **A counter-argument containing "probably", "presumably", "likely", "should", or "typically" is not a refutation.**

`unverified_assumptions` is non-empty → apply the −0.10 confidence modifier.

### 3.2 `execution` — appended by dr-repro-engineer

```json
"execution": {
  "verdict": "REPRODUCED",
  "tier": 1,
  "strategy": "PURE",
  "budget_used_s": 22,
  "commands": [
    {"cmd": "python <scratch>/repro/F03/repro.py", "cwd": "~/Documents/GitHub/Pair",
     "exit_code": 1, "duration_ms": 1840,
     "stdout_tail": "AssertionError: expected 2 tokens for 'ui-kit', got 1"}
  ],
  "differential": {"old_output": "2", "new_output": "1"},
  "reachability": {
    "caller_file": "src/api/search.ts",
    "caller_line": 88,
    "argument_provenance": "tag comes from req.query.tag, unvalidated"
  },
  "static_trace": null,
  "artifacts": ["<scratch>/repro/F03/repro.py"],
  "cleanup_verified": true
}
```

`verdict` ∈ `REPRODUCED` | `REFUTED_BY_EXECUTION` | `PARTIAL` | `NOT_RUN` | `EXEC_FAILED` | `TOOLING_ERROR`.

| Verdict | Resulting level |
|---|---|
| `REPRODUCED` + `reachability` present | L4 |
| `REPRODUCED`, no `reachability` | L3 |
| `PARTIAL` (mechanism shown on a simplified copy) | L3, and `static_trace` must state what was simplified away |
| `REFUTED_BY_EXECUTION` | dropped |
| `NOT_RUN` / `EXEC_FAILED` / `TOOLING_ERROR` | **unchanged** — keeps its pre-execution level |

> ### The asymmetry rule
> `NOT_RUN`, `EXEC_FAILED`, and `TOOLING_ERROR` carry **zero evidentiary weight**. They describe the environment, not the code. Only `REFUTED_BY_EXECUTION` may drop a finding on execution grounds. Never treat "we couldn't run it" as "it's probably fine."

### 3.3 `confidence` — computed by the orchestrator, never by an agent

Base from `evidence_level`:

| L0 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| 0.30 | 0.55 | 0.70 | 0.85 | 0.95 |

Modifiers, applied additively, then clamped to `[0.05, 0.99]`:

| Condition | Δ |
|---|---|
| `refutation.unverified_assumptions` non-empty | −0.10 |
| Detector reported truncated search (`coverage_gap: true`) | −0.05 |
| Two independent producers hit the same `(file, line±5)` | +0.05 |
| History: this `finding_hash` previously `REFUTED` | −0.20 |
| History: this `finding_hash` previously `REPRODUCED` | +0.10 |

**Never let an agent write this number.** A model emitting "0.62" produces false precision that reads as measurement. Every confidence value in a report must be reconstructable by hand from this table — that is what verification step 9 checks.

---

## 4. Run state machine

```
DETECTED → DEDUPED → ┬→ REFUTED ──────────────────────→ (dropped)
                     │
                     └→ SURVIVED → ┬→ QUEUED_EXEC → ┬→ REPRODUCED
                                   │                ├→ REFUTED_BY_EXEC → (dropped)
                                   │                ├→ PARTIAL
                                   │                └→ EXEC_FAILED
                                   │
                                   └→ SKIPPED_EXEC
                                                  ↓
                                    REPORTED → FIXING → AUDITED → COMPLETE
```

Persist the full record set to `<scratchpad>/deep-review/run-state.json` after **every** stage. A run must be inspectable and resumable without re-running detection — this is the difference between debugging the system and re-rolling it.

---

## 5. Execution classes

Assigned per changed file by `dr-runbook-probe`. Drives both strategy and the skip decision.

| Class | Meaning | Executable | Strategy | Budget |
|---|---|---|---|---|
| `PURE` | Importable, callable with literal inputs | yes | Call the changed function directly | 30s |
| `UNIT` | Reachable through an existing test harness | yes | Re-run **one** test file, filtered to one test | 60s |
| `API` | HTTP/RPC handler callable as a plain function | yes | Synthetic request object — **never start a server** | 90s |
| `UI` | Needs a renderer or browser | no | — | — |
| `DEVICE` | Needs a simulator or physical device | no | — | — |
| `BUILD` | Only observable through a build step, **or otherwise not executable in isolation** — needs a live DB, a running server, or external services | no | — | — |

Findings on `UI`/`DEVICE`/`BUILD` files skip execution entirely and route to a second, differently-framed refuter — one that attacks reachability rather than mechanism. *When you cannot buy evidence, buy scrutiny.*

Total execution wall-clock cap per run: **240s**. The scheduler spends it where it buys most — three `PURE` probes beat one `API` probe when both are queued.

---

## 6. Environment invariants

Non-negotiable, and verified on this machine:

- **`python`, never `python3`.** `python3` resolves to a Microsoft Store shim (3.14) that exits 49 silently in non-TTY subprocesses. `python` is the real 3.12.9 install.
- **`pytest` is not installed.** Python reproduction means a standalone script using `assert`/`print`, run as `python <file>`.
- **Paths as `C:/Users/...`**, never `/c/Users/...`. Git Bash handing a `/c/...` path to native `python.exe` yields `C:\c\Users\...` and ENOENT.
- **`git check-ignore -q <path>` before every write.** `.claude/` is ignored in Pair but **not** in Loom, Reverie, or pair-mobile. `node_modules/` is ignored everywhere.
- **Never `git worktree prune`.** Pair holds locked agent worktrees at `.claude/worktrees/agent-*`.
- Repos frequently sit on `main`/`master` with a clean range diff, so **the uncommitted working tree is usually the real review target.**
