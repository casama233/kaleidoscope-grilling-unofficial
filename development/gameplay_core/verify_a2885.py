"""Native saturation bounds and source-yaw spawning; native acceptance separate."""
from pathlib import Path
import subprocess,sys
from verify_a2884 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,85))
 subprocess.run(['node','--test','development/gameplay_core/test_native_saturation_bounds.mjs'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_native_saturation_source_witness.py'],cwd=ROOT,check=True)
if __name__=='__main__':main()
