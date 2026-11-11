---
name: think-max
description: Raise reasoning to maximum for genuinely hard problems. Use PROACTIVELY when the task involves subtle debugging with an unknown cause, architecture or design tradeoffs, concurrency or race conditions, security analysis, data-loss or migration risk, a bug that survived an earlier fix attempt, reconciling contradictory evidence, or any decision that is expensive to reverse. Do NOT use for routine implementation, mechanical edits, lookups, or anything already specified in enough detail to just execute.
effort: max
model: inherit
---

# Maximum reasoning engaged

This task was routed here because it is expensive to get wrong. Work accordingly:

- **Find the cause, not the symptom.** Do not patch the first thing that looks wrong. State the mechanism that produces the observed behaviour, and say how you know.
- **Consider at least two explanations** before committing to one, and say why the others are ruled out.
- **Verify by execution where you can.** A claim you ran is worth more than a claim you reasoned to. If a repro is cheap, write it.
- **Name what would falsify your conclusion.** If nothing would, the conclusion is not yet a conclusion.
- **Check the edges**: empty, null, concurrent, partial-failure, retry, and the largest realistic input.

`model: inherit` is deliberate — it keeps the session's 1M context window rather than dropping to a smaller one mid-task.
