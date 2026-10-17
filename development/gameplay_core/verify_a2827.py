"""Legacy plate cache migration is pure data evaluation, not player emulation."""
from pathlib import Path
import subprocess
from verify_a2826 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
    baseline()
    subprocess.run(['node','--test','development/gameplay_core/test_plate_food_cache.mjs'],cwd=ROOT,check=True)
    print('A2.8.27 legacy plate ranking cache PASS; full saved-world migration still unverified')
if __name__=='__main__':main()
