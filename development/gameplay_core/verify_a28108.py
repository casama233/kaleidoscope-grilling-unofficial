"""Current authored block ground proofs with finite exact Native domains."""
from pathlib import Path
import subprocess
import sys
from verify_a28107 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,108)):
    previous(expected_version=expected_version)
    subprocess.run([sys.executable,'tools/build_projectile_dodge_owned_ground.py','--check'],cwd=ROOT,check=True)
    subprocess.run(['node','--test','development/gameplay_core/test_projectile_dodge_owned_ground.mjs'],cwd=ROOT,check=True)
if __name__=='__main__':main()
