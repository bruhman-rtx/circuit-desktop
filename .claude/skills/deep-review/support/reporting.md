# deep-review shared reporting

Ranking, output contract, and the fallback. Read alongside `contracts.md`.

---

## 1. Ranking

```
rank = severity_weight × confidence

CRITICAL 1.00   HIGH 0.70   MEDIUM 0.40   LOW 0.15
```

The weights are spread wide enough that evidence never outranks severity: a `CRITICAL` at L1 scores `1.00 × 0.55 = 0.55`, a `LOW` at L4 scores `0.15 × 0.95 = 0.14`.

**Backstop:** any `CRITICAL` with confidence ≥ 0.5 sorts above every `MEDIUM` and `LOW`, regardless of score.

This is the resolution of a real tension. Ranking purely by severity is crude; ranking by evidence lets a reproduced typo outrank an argued auth bypass. Multiplication with wide weights preserves severity ordering while letting confidence break ties within a severity band. Watch it on the first few runs — if an argued `CRITICAL` ever sorts below a reproduced `MEDIUM`, the weights are wrong, not the rule.

---

## 2. ReportFindings

Call it **once**, from the main thread, with all surviving findings ranked most-severe first. Do not also print the findings as prose.

### Level → verdict

| Evidence level | `verdict` |
|---|---|
| L4, L3 | `CONFIRMED` |
| L2, L1 | `PLAUSIBLE` |
| refuted | not reported at all |

### Field mapping

| ReportFindings field | Source |
|---|---|
| `file` | `file` |
| `line` | `line` |
| `summary` | `claim` |
| `short_summary` | `claim` compressed to ≤60 chars — the claim alone, no rationale |
| `failure_scenario` | **the evidence carrier**, see below |
| `category` | `category` + `-L<level>` suffix |
| `verdict` | per the table above |

`failure_scenario` is documented as "concrete inputs/state → wrong output/crash." Observed output is a strict superset of that, so it carries the evidence:

> `tag='ui-kit' with 2 expected tokens → yields 1. Verified: python repro.py, exit 1, "AssertionError: expected 2 tokens for 'ui-kit', got 1". Reachable from src/api/search.ts:88 (req.query.tag, unvalidated).`

For an unexecuted finding, state the static chain instead:

> `Any tag containing '-' → lookup miss at src/lib/tags.ts:12. Traced from src/api/search.ts:88 → resolveTags:91 → tagIndex.get:12. Not executed (file class UI).`

The `category` suffix (`correctness-L4`, `intent-drift-L1`) is how the executed-vs-argued distinction survives, since the `verdict` enum has only two values. This is a mild abuse of a free-form field and is reversible if it reads badly.

---

## 3. The chat message

`ReportFindings` renders the cards. The accompanying message must add what the cards cannot:

1. **One decisive output line per `CONFIRMED` finding** — the actual assertion or stack line. Cap at ~5 lines total.
2. **The evidence sidecar path**, written to `<scratchpad>/deep-review/evidence.md` with full command transcripts, both worktree outputs for differentials, and each refuter's counter-argument.
3. **Degradation notice** — which stages failed, how many findings the cap dropped, how many files were excluded, and whether `dr-intent-conformance` was skipped for lack of a brief.

Do not rely on the user opening the sidecar. If a finding is confirmed, its proof appears in the message.

---

## 4. Markdown fallback

If `ReportFindings` is not in the available tool list, emit this instead and nothing else:

```markdown
| # | Severity | Conf | Lvl | File:Line | Finding |
|---|---|---|---|---|---|
| 1 | CRITICAL | 0.95 | L4 | `src/api/search.ts:88` | resolveTags drops hyphenated tags |
```

Followed by, per finding: the mechanism, the evidence (`failure_scenario` text), and the citations. Then the degradation notice from §3.

---

## 5. Reporting nothing

An empty findings array is a valid and honest result. Call `ReportFindings` with `[]` and say plainly that nothing survived, including how many candidates were refuted and at which stage.

Never pad a report to look productive. A refuter that killed everything is doing its job; a reviewer that manufactures a finding to avoid an empty result has destroyed the value of every other finding it will ever report.

---

## 6. Fix outcomes

When findings are fixed later in the same session, call `ReportFindings` **again** with the same findings, each carrying `outcome`:

| `outcome` | Meaning |
|---|---|
| `fixed` | Patch applied **and**, if a repro artifact exists, it now passes |
| `no_change_needed` | On closer inspection the code was correct |
| `skipped` | Real, but the fix is out of scope — say why |

> A fix that does not flip its own repro script from failing to passing is **not** `fixed`. Re-running the retained artifact is nearly free — the script already exists — and it is the only thing that distinguishes a fix from a plausible-looking edit.
