"""Plate-native-use arbitration and authored-yaw transitions; client separate."""
from pathlib import Path
import subprocess,sys
from verify_a2886 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,87)):
 previous(expected_version=expected_version)
 subprocess.run(['node','--test','development/gameplay_core/test_plate_use_arbitration.mjs'],cwd=ROOT,check=True)
 for name in ('test_g87_plate_use_source.py','test_plate_yaw_source_witness.py'):
  subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p',name],cwd=ROOT,check=True)
if __name__=='__main__':main()
