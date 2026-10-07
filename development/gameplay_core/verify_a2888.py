"""Harden frozen plate-use/yaw repair against transient native removal faults."""
from pathlib import Path
import subprocess,sys
from verify_a2887 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,88)):
 previous(expected_version=expected_version)
 subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_plate_cleanup_source_witness.py'],cwd=ROOT,check=True)
if __name__=='__main__':main()
