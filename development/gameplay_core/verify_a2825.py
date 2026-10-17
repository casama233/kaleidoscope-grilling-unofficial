"""Core skewer storage and event regression checks; no player/client claim."""
from pathlib import Path
import subprocess,sys
from verify_a2821 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
    baseline()
    subprocess.run(['node','--test','development/gameplay_core/test_core_skewer_cycle.mjs'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'tools/build_grilling_guide.py','--check'],cwd=ROOT,check=True)
    print('A2.8.25 core skewer source/storage/event regressions PASS; client acceptance remains open')
if __name__=='__main__':main()
