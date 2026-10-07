"""Source-backed asynchronous oil ownership and Cookery damage/feedback repairs."""
from verify_a2879 import main as previous
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[2]

def main():
    previous(expected_version=(2,8,83))
    subprocess.run(['node','--test','development/gameplay_core/test_oil_snapshot_intent.mjs','development/gameplay_core/test_cookery_damage_feedback.mjs'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'tools/build_cookery_effect_feedback.py','--check'],cwd=ROOT,check=True)

if __name__=='__main__':
    main()
