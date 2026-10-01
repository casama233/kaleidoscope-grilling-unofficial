"""Native seasoning stack conservation; source/storage doubles are not players."""
from pathlib import Path
import subprocess
from verify_a2820 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
    baseline()
    subprocess.run(['python','tools/check_station_storage.py'],cwd=ROOT,check=True)
    print('A2.8.21 native seasoning storage PASS; not client/live migration acceptance')
if __name__=='__main__':main()
