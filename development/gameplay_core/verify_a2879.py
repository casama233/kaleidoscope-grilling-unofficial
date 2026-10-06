"""Same-event rack ray targeting with preserved direct-touch semantics."""
from verify_a2878 import main as previous
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,79))
 subprocess.run(['node','--test','development/gameplay_core/test_rack_aim_hit.mjs'],cwd=ROOT,check=True)
if __name__=='__main__':main()
