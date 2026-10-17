"""Oil-machine loss/duplication and active-registry regression gate."""
from pathlib import Path
import subprocess
from verify_a2818 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
    baseline()
    subprocess.run(['node','--test','development/gameplay_core/test_oil_transactions.mjs'],cwd=ROOT,check=True)
    print('A2.8.19 oil transaction/storage tests PASS; not native client or live migration acceptance')
if __name__=='__main__':main()
