"""QA-only binary-board rendering follow-on; production data stays conserved."""
from pathlib import Path
import subprocess,sys
from verify_a2890 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,95))
 subprocess.run(['node','--test','development/gameplay_core/test_plate_held_qa.mjs'],cwd=ROOT,check=True)
 for name in ['test_plate_client_probe.py','test_g91_source_conservation.py','test_g92_source_conservation.py','test_g93_source_conservation.py','test_g94_source_conservation.py','test_g95_source_conservation.py']:
  subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p',name],cwd=ROOT,check=True)
if __name__=='__main__':main()
