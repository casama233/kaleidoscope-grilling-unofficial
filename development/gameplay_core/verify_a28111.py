"""Accepted ingredient-count transactions plus exactly reviewed first-person pose."""
from pathlib import Path
import subprocess
import sys
from verify_a28110 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,111)):
    previous(expected_version=expected_version)
    subprocess.run([sys.executable,'development/gameplay_core/test_bottle_pose_review.py'],cwd=ROOT,check=True)
    print('G111 ingredient-count and exact pose source gates PASS; full native candidate acceptance remains pending')
if __name__=='__main__':main()
