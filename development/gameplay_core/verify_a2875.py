"""G75 reconciles published G73 and preserved bottle/rack/plate repairs."""
from pathlib import Path
import subprocess,sys
from verify_a2871 import main as bottle_checks
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,75)):
 bottle_checks(expected_version=expected_version)
 sys.path.insert(0,str(ROOT/'tools'))
 from check_cookery160_host import check
 check()
 subprocess.run(['node','--experimental-vm-modules','--test','development/gameplay_core/test_java_heat_deadlines.mjs'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'tools/test_g75_source_conservation.py'],cwd=ROOT,check=True)
 subprocess.run(['node','--test','development/gameplay_core/test_ordinary_java_feedback.mjs'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_java_custom_skewer_gui.py'],cwd=ROOT,check=True)
 print('G75 combined source checks PASS; compiled/native/migration gates remain separate')
if __name__=='__main__':main()
