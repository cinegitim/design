#!/usr/bin/env python3
"""Convenience wrapper: render + QA + package the Burs Dosyası / 001 bundle."""
import subprocess, sys
from pathlib import Path
APP = Path(__file__).resolve().parent
steps = [['python3', 'build.py'], ['python3', 'deliver.py']]
for cmd in steps:
    print('+', ' '.join(cmd))
    sys.exit(subprocess.run(cmd, cwd=APP).returncode or 0)
