"""G109 current-main bottle grip and retained seasoning ingredient lore."""
from pathlib import Path
import subprocess
import sys
from verify_a28108 import main as previous
ROOT = Path(__file__).resolve().parents[2]
def main():
    previous(expected_version=(2, 8, 109))
    subprocess.run([sys.executable, 'development/gameplay_core/test_bottle_pose_review.py'], cwd=ROOT, check=True)
    subprocess.run(['node', '--test', 'development/gameplay_core/test_seasoning_ingredient_lore.mjs'], cwd=ROOT, check=True)
    print('G109 exact pose scope and ingredient lore PASS; native acceptance remains pending')
if __name__ == '__main__':
    main()
