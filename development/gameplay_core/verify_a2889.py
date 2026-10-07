"""Source-calibrated plate facing and canonical full ordinary mesh; client separate."""
from pathlib import Path
import subprocess,sys
from verify_a2888 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,89)):
 previous(expected_version=expected_version)
 subprocess.run([sys.executable,'development/gameplay_core/test_plate_food_display.py'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_plate_g89_source_witness.py'],cwd=ROOT,check=True)
if __name__=='__main__':main()
