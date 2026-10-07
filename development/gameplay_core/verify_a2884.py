"""Plate body alignment and opt-in reward diagnosis; no nutrition repair claim."""
from pathlib import Path
import subprocess,sys
from verify_a2883 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,84))
 subprocess.run(['node','--test','development/gameplay_core/test_plate_reward_qa.mjs'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_plate_reward_qa_source_witness.py'],cwd=ROOT,check=True)
if __name__=='__main__':main()
