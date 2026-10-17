"""Compatibility entry: the guide is part of the canonical Grilling pack."""
from pathlib import Path
import runpy
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "development/gameplay_core"))
if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1]/"development/gameplay_core/verify_current.py"),run_name="__main__")
