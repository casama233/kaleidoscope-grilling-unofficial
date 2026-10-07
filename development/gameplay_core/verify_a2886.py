"""Exact current-main palette and plate union; client evidence stays scoped."""
from pathlib import Path
import subprocess,sys
from verify_a2885 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,86))
 subprocess.run([sys.executable,'tools/test_g86_source_coherence.py'],cwd=ROOT,check=True)
if __name__=='__main__':main()
