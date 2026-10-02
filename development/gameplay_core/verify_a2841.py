"""Audit-driven effect lifecycle, heat precision, metadata projection and bounded workers."""
from pathlib import Path
import subprocess
from verify_a2840 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
 baseline()
 subprocess.run(['node','--test','development/gameplay_core/test_parity_review.mjs'],cwd=ROOT,check=True)
 print('A2.8.41 audit repair source regressions PASS; native BDS, human client and saved-world gates remain independent')
if __name__=='__main__':main()
