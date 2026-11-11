#!/usr/bin/env python
"""deep-review telemetry: append-only run/finding log, history lookup, derived stats.

Invoked by the deep-review skills. Never affects a run's outcome -- every path
fails open and exits 0.

Modes:
  record  --repo <path>              read JSON from stdin, append to the repo's log
  history --repo <path> --hashes a,b  emit {hash: {refuted: n, reproduced: n}}
  stats   --repo <path> [--last N]    emit derived metrics

Usage:
  echo '{"kind":"finding",...}' | python telemetry.py record --repo C:/path/to/repo
  python telemetry.py history --repo C:/path/to/repo --hashes a3f1,b7c2
  python telemetry.py stats --repo C:/path/to/repo
"""
import argparse
import collections
import json
import os
import re
import sys
import time

TELEM_DIR = os.path.join(os.path.expanduser("~"), ".claude", "review-telemetry")
MAX_BYTES = 8 * 1024 * 1024          # rotate past this
KEEP_ROTATIONS = 2


def slug(s):
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(s))[:128]


def log_path(repo):
    name = slug(os.path.basename(os.path.abspath(repo.rstrip("/\\"))) or "unknown")
    return os.path.join(TELEM_DIR, name + ".jsonl")


def rotate_if_needed(path):
    try:
        if os.path.getsize(path) < MAX_BYTES:
            return
        for i in range(KEEP_ROTATIONS - 1, 0, -1):
            src, dst = "%s.%d" % (path, i), "%s.%d" % (path, i + 1)
            if os.path.exists(src):
                os.replace(src, dst)
        os.replace(path, path + ".1")
    except OSError:
        pass


def read_records(path):
    """Yield records from the current log and its rotations, oldest first."""
    files = ["%s.%d" % (path, i) for i in range(KEEP_ROTATIONS, 0, -1)] + [path]
    for f in files:
        if not os.path.exists(f):
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except ValueError:
                        continue          # skip a torn line, keep going
        except OSError:
            continue


# ---------------------------------------------------------------- modes

def m_record(args):
    raw = sys.stdin.read().strip()
    if not raw:
        return
    try:
        payload = json.loads(raw)
    except ValueError:
        return
    records = payload if isinstance(payload, list) else [payload]

    now = int(time.time())
    path = log_path(args.repo)
    os.makedirs(TELEM_DIR, exist_ok=True)
    rotate_if_needed(path)

    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        for rec in records:
            if not isinstance(rec, dict):
                continue
            rec.setdefault("ts", now)
            rec.setdefault("kind", "finding")
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def m_history(args):
    """Prior outcomes per finding_hash, for the confidence modifiers in contracts.md."""
    wanted = {h.strip() for h in (args.hashes or "").split(",") if h.strip()}
    counts = collections.defaultdict(lambda: {"refuted": 0, "reproduced": 0, "seen": 0})

    for rec in read_records(log_path(args.repo)):
        h = rec.get("finding_hash")
        if not h or (wanted and h not in wanted):
            continue
        c = counts[h]
        c["seen"] += 1
        chain = rec.get("state_chain") or []
        if "REFUTED" in chain or "REFUTED_BY_EXEC" in chain:
            c["refuted"] += 1
        if "REPRODUCED" in chain:
            c["reproduced"] += 1

    out = {}
    for h, c in counts.items():
        # contracts.md: previously REFUTED -> -0.20 ; previously REPRODUCED -> +0.10
        delta = 0.0
        if c["refuted"]:
            delta -= 0.20
        if c["reproduced"]:
            delta += 0.10
        out[h] = {"seen": c["seen"], "refuted": c["refuted"],
                  "reproduced": c["reproduced"], "confidence_delta": round(delta, 2)}
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


def m_stats(args):
    findings, runs = [], []
    for rec in read_records(log_path(args.repo)):
        (runs if rec.get("kind") == "run" else findings).append(rec)
    if args.last:
        findings, runs = findings[-args.last:], runs[-args.last:]

    by_producer = collections.defaultdict(lambda: {"produced": 0, "survived": 0,
                                                   "reproduced": 0, "reported": 0})
    exec_attempted = exec_succeeded = refuted = 0

    for f in findings:
        chain = f.get("state_chain") or []
        p = by_producer[f.get("producer", "unknown")]
        p["produced"] += 1
        if "SURVIVED" in chain:
            p["survived"] += 1
        if "REPRODUCED" in chain:
            p["reproduced"] += 1
        if "REPORTED" in chain:
            p["reported"] += 1
        if "REFUTED" in chain:
            refuted += 1
        if "QUEUED_EXEC" in chain:
            exec_attempted += 1
            if "REPRODUCED" in chain or "REFUTED_BY_EXEC" in chain:
                exec_succeeded += 1

    def pct(n, d):
        return round(100.0 * n / d, 1) if d else None

    total = len(findings)
    out = {
        "repo": os.path.basename(os.path.abspath(args.repo.rstrip("/\\"))),
        "runs": len(runs),
        "findings_logged": total,
        "refuter_kill_rate_pct": pct(refuted, total),
        "execution_success_rate_pct": pct(exec_succeeded, exec_attempted),
        "detector_precision_pct": {
            name: pct(v["survived"], v["produced"]) for name, v in sorted(by_producer.items())
        },
        "detector_volume": {name: v["produced"] for name, v in sorted(by_producer.items())},
        "reproduction_rate_pct": pct(
            sum(v["reproduced"] for v in by_producer.values()), total),
        "fix_success": collections.Counter(
            f.get("outcome") for f in findings if f.get("outcome")),
    }
    out["fix_success"] = dict(out["fix_success"])

    notes = []
    if total < 20:
        notes.append("Fewer than 20 findings logged -- these rates are not yet meaningful.")
    kr = out["refuter_kill_rate_pct"]
    if kr is not None and kr > 70:
        notes.append("Refuter kill rate above 70%% (%.1f%%) -- likely miscalibrated, "
                     "check whether it is refuting on unverified assumptions." % kr)
    out["notes"] = notes

    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


MODES = {"record": m_record, "history": m_history, "stats": m_stats}


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("mode", choices=sorted(MODES))
    ap.add_argument("--repo", required=True)
    ap.add_argument("--hashes", default="")
    ap.add_argument("--last", type=int, default=0)
    args = ap.parse_args()
    MODES[args.mode](args)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    except Exception:
        pass
    try:
        main()
    except Exception as e:                      # never break a review run
        sys.stderr.write("telemetry: %s\n" % e)
    finally:
        sys.exit(0)
