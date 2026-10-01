"""Rack item conservation and public-tag regression gate."""
from pathlib import Path
import subprocess
from verify_a2819 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
    baseline()
    subprocess.run(['node','--test','development/gameplay_core/test_rack_transactions.mjs'],cwd=ROOT,check=True)
    print('A2.8.20 rack transactions/tags PASS; not native client or live migration acceptance')
if __name__=='__main__':main()
