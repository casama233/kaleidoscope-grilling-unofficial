"""Current-main/placed repair consolidation and held-only plate contents."""
from pathlib import Path
import subprocess,sys
from verify_a2889 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,90)):
 previous(expected_version=expected_version)
 subprocess.run(['node','--test','development/gameplay_core/test_plate_held_visual.mjs','development/gameplay_core/test_bottle_held_visual.mjs','development/gameplay_core/test_integration_interfaces.mjs'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'tools/build_plate_held.py','--check'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_plate_held_assets.py'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_g90_source_conservation.py'],cwd=ROOT,check=True)
if __name__=='__main__':main()
