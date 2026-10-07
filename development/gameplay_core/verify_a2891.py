"""Native-observed Cloud parser repair; runtime remains source-conserved."""
from pathlib import Path
import subprocess,sys
from verify_a2890 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,91))
 subprocess.run(['node','--test','development/gameplay_core/test_plate_held_qa.mjs'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_g91_source_conservation.py'],cwd=ROOT,check=True)
if __name__=='__main__':main()
