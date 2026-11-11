---
name: think-light
description: Drop reasoning to minimum for trivial, fully-specified work. Use PROACTIVELY when the task is a typo fix, a rename, reformatting, bumping a version string, adding an import, answering a direct factual question about a file already read, listing or finding files, or any single edit where the exact change is already stated and no judgment is required. Do NOT use when anything must be decided, debugged, designed, reviewed, or verified for correctness.
effort: low
model: inherit
---

# Minimum reasoning engaged

This task was routed here because it is mechanical. Do it directly and stop.

- Make the stated change. Do not redesign, refactor, or improve surrounding code.
- Do not add tests, docs, or error handling that was not asked for.
- One or two sentences of response is the right length.

**Escape hatch:** if the task turns out not to be trivial — the change is ambiguous, it touches more than expected, or something looks wrong — say so and stop. Do not push a low-effort answer through a problem that deserves more.
