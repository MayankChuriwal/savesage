#!/usr/bin/env python3
"""Rebuild everything in out/ from raw/. No network except the report's spot-check.

Order matters: parse -> parse_calc -> parse_hubs -> merge -> report.
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
for step in ("parse.py", "parse_calc.py", "parse_hubs.py", "merge.py", "report.py"):
    print(f"\n=== {step} ===")
    r = subprocess.run([sys.executable, os.path.join(HERE, step)])
    if r.returncode:
        sys.exit(f"{step} failed")
print("\nbuild complete")
