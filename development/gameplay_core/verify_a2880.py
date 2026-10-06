"""Rack jar model-space projection; unchanged G79 interaction/ownership gates."""
from verify_a2879 import main as previous
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,80))
 subprocess.run([sys.executable,'development/gameplay_core/build_direct_rack_geometry.py','--check'],cwd=ROOT,check=True)
if __name__=='__main__':main()
