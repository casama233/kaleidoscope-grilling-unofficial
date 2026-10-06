"""G75 preserves Java ordered legacy seasonings and output ownership on write faults."""
from pathlib import Path
import subprocess
from verify_a2874 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,75))
 subprocess.run(['node','--experimental-vm-modules','--test','development/gameplay_core/test_legacy_seasoning_heat_merge.mjs'],cwd=ROOT,check=True)
if __name__=='__main__':main()
