#!/usr/bin/env python3
"""2.8.8 is a safety candidate, not the historical simulated-interaction suite."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
subprocess.run([sys.executable,str(ROOT/'tools/family_candidate.py')],check=True)
subprocess.run(['node',str(ROOT/'tools/check_family_knives.mjs')],cwd=ROOT,check=True)
