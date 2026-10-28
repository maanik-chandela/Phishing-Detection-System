#!/usr/bin/env python3
"""
Reproducible experiment runner for the balanced research splits.

Runs:
1. Split validation audit
2. URL-only baseline (uses existing script logic)
3. HTML-only baseline
4. Hybrid URL+HTML baseline
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, cmd: list[str]) -> int:
    print(f"\n{'=' * 60}")
    print(f"STEP: {name}")
    print(f"CMD: {' '.join(cmd)}")
    print(f"{'=' * 60}\n")
    result = subprocess.run(cmd, cwd=str(ROOT))
    print(f"\n[{name}] exit code: {result.returncode}")
    return result.returncode


def main() -> int:
    steps = [
        ("audit_splits", [sys.executable, "-m", "scripts.audit_splits"]),
        ("url_baseline_balanced", [sys.executable, "-m", "scripts.train_url_baseline_balanced"]),
        ("html_baseline_balanced", [sys.executable, "-m", "scripts.train_html_baseline_balanced"]),
        ("hybrid_baseline_balanced", [sys.executable, "-m", "scripts.train_hybrid_baseline_balanced"]),
    ]

    failures = []
    for name, cmd in steps:
        rc = run_step(name, cmd)
        if rc != 0:
            failures.append((name, rc))

    if failures:
        print("\nFAILED STEPS:")
        for name, rc in failures:
            print(f"  - {name}: {rc}")
        return 1

    print("\nAll experiment steps completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
