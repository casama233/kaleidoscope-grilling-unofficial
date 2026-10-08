"""Current Java pending completion and finish audio dispatch."""
from pathlib import Path
import subprocess
from verify_a28108 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,109)):
    previous(expected_version=expected_version)
    subprocess.run(['node','--test','development/gameplay_core/test_pending_completion_source.mjs'],cwd=ROOT,check=True)
if __name__=='__main__':main()
