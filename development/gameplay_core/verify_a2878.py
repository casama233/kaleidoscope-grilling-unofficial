"""Coherent corrected rack/plate/heat and ordered-seasoning/output ownership source."""
from pathlib import Path
import subprocess,sys
from verify_a2874 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,78)):
 previous(expected_version=expected_version)
 subprocess.run(['node','--experimental-vm-modules','--test','development/gameplay_core/test_legacy_seasoning_heat_merge.mjs'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'tools/test_g75_source_conservation.py'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_java_custom_skewer_gui.py'],cwd=ROOT,check=True)
if __name__=='__main__':main()
